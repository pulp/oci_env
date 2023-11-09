import os
import pathlib
import subprocess
import time

from urllib import request

from oci_env.logger import logger


def get_oci_env_path():
    """This returns the root directory of the oci-env checkout."""

    if OCI_ENV_PATH := os.environ.get("OCI_ENV_PATH"):
        OCI_ENV_PATH = OCI_ENV_PATH.rstrip('/')
        logger.info(f'USING OCI_ENV_PATH FROM ENV: {OCI_ENV_PATH}')
        return OCI_ENV_PATH

    # this is the $CHECKOUT/client/oci_env/utils.py path ...
    path = os.path.dirname(__file__)

    # use git to find the root dir ...
    pid = subprocess.run(
        "git rev-parse --show-toplevel",
        cwd=path,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if pid.returncode != 0:
        cwd = os.getcwd().rstrip('/')
        logger.warning(f'USING CWD {cwd} FOR OCI_ENV_PATH BECAUSE OF GIT CMD FAILURE {pid.stdout}')
        return cwd

    gitroot = pid.stdout.decode('utf-8').strip().rstrip('/')
    logger.info(f'USING {gitroot} FOR OCI_ENV_PATH BASED ON GIT CMD OUTPUT')
    return gitroot


def exit_with_error(msg):
    logger.error(msg)
    exit(1)


def read_env_file(path, exit_on_error=True):
    """
    Read the contents of a .env file into a dictionary.
    """
    result = {}

    try:
        with open(path, "r") as f:
            for line in f:
                if not line.startswith("#") and "=" in line:
                    key, val = line.split("=", maxsplit=1)

                    result[key.strip("' \"")] = val.strip("' \"\n")

    except FileNotFoundError:
        if exit_on_error:
            exit_with_error(f"Environment file at {path} does not exist.")

    return result


def get_config(env_file):
    """
    Parse the compose.env file and return any defaults that aren't set there.
    """
    path = get_oci_env_path()

    # These values shouldn't be edited by the user and have the highest precedence.
    constant_vals = {
        "OCI_ENV_DIR": path,
        "OCI_ENV_CONFIG_FILE": env_file,
    }

    user_preferences = read_env_file(env_file)

    # default values
    config = {
        # List of : separated projects to install from source
        "DEV_SOURCE_PATH": "",

        # Directory on the host where the DEV_SOURCE_PATH projects are checked out
        "SRC_DIR": os.path.abspath(os.path.join(path, "..")),

        # List of : separated profiles to use
        "COMPOSE_PROFILE": "",

        # Django admin credentials
        "DJANGO_SUPERUSER_USERNAME": "admin",
        "DJANGO_SUPERUSER_PASSWORD": "password",

        # Test fixtures
        "REMOTE_FIXTURES_ORIGIN": "https://fixtures.pulpproject.org/",

        # API URL
        "API_PROTOCOL": "http",
        "API_HOST": "localhost",
        "API_PORT": "5001",

        # A port dedicated for exposing generated docs
        "DOCS_PORT": "12345",
        "NGINX_DOCS_PORT": user_preferences.get("DOCS_PORT", "12345"),

        # nginx port to run in the container. This defaults to 5001 if nothing is set or
        # the value of API_HOST if that is set.
        "NGINX_PORT": user_preferences.get("API_PORT", "5001"),
        "NGINX_SSL_PORT": "443",

        # Project name to use for compose
        "COMPOSE_PROJECT_NAME": "oci_env",

        # Container runtime to use.
        "COMPOSE_BINARY": "podman",

        # Containers where the various pulp services are running
        "API_CONTAINER": "pulp",
        "DB_CONTAINER": "pulp",
        "CONTENT_APP_CONTAINER": "pulp",
        "WORKER_CONTAINER": "pulp",
    }

    # override any defaults that the user set.
    cfg = {**config, **user_preferences, **constant_vals}

    # allow env overrides except for constants
    for key in sorted(list(cfg.keys())):
        if key in os.environ and key not in constant_vals:
            val = os.environ.get(key)
            cfg[key] = val
        else:
            val = cfg[key]

    return cfg


def parse_profiles(config):
    """
    Load the profiles defined in COMPOSE_PROFILE
    """
    profiles = config["COMPOSE_PROFILE"].split(":")
    oci_env_path = get_oci_env_path()
    src_path = config["SRC_DIR"]
    compiled_path = os.path.join(oci_env_path, ".compiled", config["COMPOSE_PROJECT_NAME"])

    pathlib.Path(compiled_path).mkdir(parents=True, exist_ok=True)

    profile_paths = [
        {
            "path": os.path.join(oci_env_path, "base"),
            "name": "base",
            "container_path": os.path.join(
                "/opt/oci_env",
                "base"
            )
        },
    ]

    # parse the profiles and ensure that all of them exist.
    for profile in profiles:
        if "/" in profile:
            plugin, name = profile.split("/", maxsplit=1)

            profile_path = os.path.abspath(
                os.path.join(src_path, plugin, "profiles", name)
            )
            container_path = os.path.join(
                "/src",
                plugin,
                "profiles",
                name,
            )
        else:
            plugin = "oci_env"
            name = profile
            profile_path = os.path.join(oci_env_path, "profiles", name)

            # oci env profiles are loaded from "/opt/oci_env"
            container_path = os.path.join(
                "/opt/oci_env",
                "profiles",
                name
            )

        if not os.path.isdir(profile_path):
            exit_with_error(f"{profile} from COMPOSE_PROFILE does not exist at {profile_path}")

        profile_paths.append({
            "path": profile_path,
            "name": profile,
            "container_path": container_path
        })

    init_script = [
        "#!/bin/bash",
        "",
        "# AUTOGENERATED by oci-env",
        "# This script runs automatically when the container starts.",
        ""
    ]

    env_output = []

    compose_files = []

    profile_defaults = {}

    # Compile the information in the compose profiles into .compiled.
    for profile in profile_paths:
        init_file = os.path.join(profile["path"], "init.sh")
        env_file = os.path.join(profile["path"], "pulp_config.env")
        compose_file = os.path.join(profile["path"], "compose.yaml")
        profile_requirements_file = os.path.join(profile["path"], "profile_requirements.txt")
        config_defaults_file = os.path.join(profile["path"], "profile_default_config.env")

        # Ensure profile dependencies are in correct order
        try:
            with open(profile_requirements_file, "r") as f:

                for line in f:
                    req_profile = line.strip()
                    if req_profile.startswith("#") or req_profile == "":
                        continue

                    if req_profile not in config["COMPOSE_PROFILE"].split(profile["name"])[0]:
                        exit_with_error(f"\"{req_profile}\" is required to be in your COMPOSE_PROFILE config before \"{profile['name']}\"")

        except FileNotFoundError:
            pass

        # Add any init scripts to .compiled/init.sh.
        if os.path.isfile(init_file):
            script_path = os.path.join(profile['container_path'], "init.sh")
            init_script.append(f"bash {script_path}")

        # Update config used when formatting {VAR} templates with profile's defaults
        # Ensure user config takes priority, but allows profiles to override their dependencies defaults
        profile_defaults.update(read_env_file(config_defaults_file, exit_on_error=False))
        updated_config = {**profile_defaults, **config}

        # Combine all of the pulp_config.env files into .compiled/combined.env. Format
        # all the {VAR} templates.
        try:
            with open(env_file, "r") as f:
                for line in f:
                    try:
                        env_output.append(line.strip().format(**updated_config))
                    except KeyError as e:
                        exit_with_error(
                            f"{env_file} contains variable {e}, which is not "
                            "defined in your .compose.env. This value is required to "
                            "be set."
                        )
        except FileNotFoundError:
            pass

        # Copy any compose files into .compiled and format any variables in them.
        try:
            with open(compose_file, "r") as f:
                data = f.read()

                try:
                    data = data.format(**updated_config)
                except KeyError as e:
                    exit_with_error(
                        f"{compose_file} contains variable {e}, which is not "
                        "defined in your compose.env. This value is required to "
                        "be set."
                    )

                compose_file = profile["name"].replace("/", "_")
                compose_file = compose_file + "_compose.yaml"
                compose_file = os.path.join(compiled_path, compose_file)

                compose_files.append(compose_file)

                with open(compose_file, "w") as out_file:
                    out_file.write(data)

        except FileNotFoundError:
            pass

    with open(os.path.join(compiled_path, "init.sh"), "w") as f:
        f.write("\n".join(init_script))

    with open(os.path.join(compiled_path, "combined.env"), "w") as f:
        f.write("\n".join(env_output))

    # Update config with new profile defaults (a side effect)
    for key, value in profile_defaults.items():
        config.setdefault(key, value)

    return compose_files


def get_env_file(path, env_file):
    if env_file == "":
        files = [
            os.path.join(path, "compose.env"),
            os.path.join(path, ".compose.env"),
        ]

        for f in files:
            if os.path.isfile(f):
                return f
        logger.error(f"No compose.env or .compose.env file found in {path}.")

    else:
        files = [
            os.path.abspath(env_file),
            os.path.join(os.getcwd(), env_file),
        ]

        for f in files:
            if os.path.isfile(f):
                return f
        logger.error(f"Could not find file {env_file}")

    exit(1)


def exit_if_failed(rc):
    if rc != 0:
        exit(rc)


class Compose:
    """
    This provides an interface to docker/podman compose for running compose commands
    and executing scripts inside running containers.
    """
    def __init__(self, is_verbose, env_file):
        self.path = get_oci_env_path()
        self.config = get_config(get_env_file(self.path, env_file))
        self.compose_files = parse_profiles(self.config)
        self.is_verbose = is_verbose

        if self.is_verbose:
            for key in sorted(self.config.keys()):
                logger.info(f'OCI CFG {key} = {self.config[key]}')

    def compose_command(self, cmd, interactive=False, pipe_output=False):
        """
        Run a docker-compose or podman-compose command.

        This sets the correct project name and loads up all the compose files, but
        takes in the rest of the arguments (exec, up, down, etc) from the user.
        """
        binary = [self.config["COMPOSE_BINARY"] + "-compose", "-p", self.config["COMPOSE_PROJECT_NAME"]]

        compose_files = []

        for f in self.compose_files:
            compose_files.append("-f")
            compose_files.append(f)

        cmd = binary + compose_files + cmd

        if interactive:
            if self.is_verbose:
                logger.info(f"Running [interactive] command in container: {' '.join(cmd)}")
            return subprocess.call(cmd)
        else:
            if self.is_verbose:
                logger.info(f"Running [non-interactive] command in container: {' '.join(cmd)}")
            return subprocess.run(cmd, capture_output=pipe_output)

    def container_name(self, service=None):
        """Docker compose name containers using `-` while podman uses `_`

        Underlying bash code:
            binary ps -q --filter name=oci_env
            --format '{{.Names}}' | grep env | grep -E '.1$'
        """
        binary = self.config["COMPOSE_BINARY"]
        service = service or self.config["API_CONTAINER"]
        project_name = self.config['COMPOSE_PROJECT_NAME']

        def _exit_no_container_found():
            service_name = service if service[-1].isdigit() else f"{service}_1"
            name = f"{project_name}_{service_name}"
            logger.error(
                f"Could not find a running container named: {name} \n"
                f"instead of {service!r} did you mean 'pulp' or 'ui'?\n"
                "Run `oci-env compose ps` to see all running containers."
            )
            exit(1)

        def _service_containers():
            """# Grep for the service name. e.g: pulp"""
            return subprocess.Popen(
                ("grep", service),
                stdin=running_containers.stdout,
                stdout=subprocess.PIPE
            )

        # List all containers that match the PROJECT_NAME pattern. e.g: oci_env
        #   WARNING: Ignoring custom format, because both --format and --quiet are set.
        cmd = [binary, "ps", "--filter", f"name={project_name}", "--format", "{{.Names}}"]
        running_containers = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        # Does the user passed a specific container number? e.g: `oci-env exec -s pulp-2 ls`
        if service[-1].isdigit():
            container_name = _service_containers().stdout.read().decode("utf-8").strip().split("\n")[0]
            if service in container_name:
                return container_name

        # Else grep only the container ending with `_1` or `-1` (the main service)
        try:
            return subprocess.check_output(
                ("grep", '-E', ".1$"),
                stdin=_service_containers().stdout
            ).decode("utf-8").strip().split("\n")[0]
        except subprocess.CalledProcessError:
            _exit_no_container_found()

    def exec(self, args, service=None, interactive=False, pipe_output=False, privileged=False):
        """
        Execute a script in a running container using podman or docker.

        This uses podman or docker directly rather than attempting to use
        docker/podman-compose since the information returned from the process
        differs between podman-compose and docker-compose.
        """
        service = service or self.config["API_CONTAINER"]
        binary = self.config["COMPOSE_BINARY"]

        # docker fails on systems with no interactive CLI. This tells docker
        # to use a pseudo terminal when no CLI is available.
        if os.getenv("COMPOSE_INTERACTIVE_NO_CLI", "0") == "1":
            cmd = [binary, "exec", self.container_name(service)] + args
        else:
            cmd = [binary, "exec", "-it", self.container_name(service)] + args

        if privileged:
            cmd = cmd[:2] + ["--privileged"] + cmd[2:]

        if interactive:
            if self.is_verbose:
                logger.info(f"Running [interactive] command in container: {' '.join(cmd)}")
            proc = subprocess.call(cmd)
        else:
            if self.is_verbose:
                logger.info(f"Running [non-interactive] command in container: {' '.join(cmd)}")
            proc = subprocess.run(cmd, capture_output=pipe_output)
        return proc

    def get_dynaconf_variable(self, name):
        """
        Get the value of a configuration from dynaconf.
        """

        return self.exec_container_script("get_dynaconf_var.sh", args=[name], pipe_output=True).stdout.decode().strip()

    def exec_container_script(self, script, args=None, interactive=False, pipe_output=False, privileged=False):
        """
        Executes a script from the base/container_scripts/ directory in the container.
        """

        args = args or []
        script_path = f"/opt/oci_env/base/container_scripts/{script}"
        cmd = ["bash", script_path] + args

        return self.exec(cmd, interactive=interactive, pipe_output=pipe_output, privileged=privileged)

    def dump_container_logs(self, container_name):
        binary = self.config["COMPOSE_BINARY"]
        cmd = [binary, "logs", container_name]
        pid = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        print('*' * 100)
        print(f'{container_name} log dump ...')
        print('*' * 100)
        print(pid.stdout.decode("utf-8"))
        print('*' * 100)

    def poll(self, attempts, wait_time):
        status_api = ""

        container_name = self.container_name()

        for i in range(attempts):
            print(f"Waiting for [{container_name}] API to start (attempt {i+1} of {attempts})")
            # re request the api root each time because it's not alwasy available until the
            # app boots
            api_root = self.get_dynaconf_variable("API_ROOT")
            status_api = "{}://{}:{}{}api/v3/status/".format(
                self.config["API_PROTOCOL"],
                self.config["API_HOST"],
                self.config["API_PORT"],
                api_root,
            )
            try:
                if request.urlopen(status_api).code == 200:
                    logger.info(f"[{container_name}] {status_api} online after {(i * wait_time)} seconds")
                    return
            except:
                time.sleep(wait_time)

        # give the user some context as to why polling failed ...
        self.dump_container_logs(container_name)

        exit_with_error(f"Failed to start [{container_name}] {status_api} after {attempts * wait_time} seconds")
