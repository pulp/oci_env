import subprocess
import os
import time
import pathlib

from urllib import request

from oci_env.utils import exit_if_failed, exit_with_error
from oci_env.templates import profile_templates


def compose(args, client):
    client.compose_command(args.command, interactive=True)


def exec(args, client):
    client.exec(args.command, interactive=True, service=args.service)


def db(args, client):
    action = str(args.action[0])
    if action == 'reset':
        api_root = client.get_dynaconf_variable("API_ROOT")
        status_api = "{}://{}:{}{}api/v3/status/".format(
            client.config["API_PROTOCOL"],
            client.config["API_HOST"],
            client.config["API_PORT"],
            api_root,
        )

        exit_if_failed(
            client.exec_container_script(
                f"database_reset.sh",
                args=None,
                interactive=True)
        )

        for i in range(10):
            print(f"Waiting for API to restart (attempt {i+1} of 10)")
            try:
                if request.urlopen(status_api).code == 200:
                    print("Back online")
                    return
            except:
                pass

            time.sleep(5)
        
        exit_with_error("Failed to restart")

    else:
        raise Exception(f'db {args.action} not implemented')


def shell(args, client):
    cmd = []
    if args.shell == "bash":
        cmd = ["bash"]
    elif args.shell == "python":
        cmd = ["pulpcore-manager", "shell_plus"]
    elif args.shell == "db":
        cmd = ["pulpcore-manager", "dbshell"]
    else:
        exit_with_error("Unsupported shell")

    client.exec(cmd, interactive=True)


def test(args, client):
    if args.install_deps:
        test_script = f"install_{args.test}_requirements.sh"

        if args.plugin:
            exit_if_failed(client.exec_container_script(test_script, args=[args.plugin]).returncode)
        else:
            for project in client.config["DEV_SOURCE_PATH"].split(":"):
                exit_if_failed(client.exec_container_script(test_script, args=[project]).returncode)

    if args.plugin:
        exit_if_failed(
            client.exec_container_script(
                f"run_{args.test}_tests.sh",
                args=[args.plugin] + args.args,
                interactive=True)
        )


def generate_client(args, client):
    api_root = client.get_dynaconf_variable("API_ROOT")

    base_cmd = [
        "bash",
        os.path.join(client.path, "base", "local_scripts", "generate_client.sh"),
    ]

    if args.plugin:
        plugins = [args.plugin,]
    else:
        plugins = client.config["DEV_SOURCE_PATH"].split(":")

    env = {**os.environ, **client.config, "PULP_API_ROOT": api_root}

    for plugin in plugins:
        cmd = base_cmd + [plugin, ]
        if args.is_verbose:
            print(f"Running local command: {' '.join(cmd)}")

        exit_if_failed(subprocess.run(cmd, env=env, cwd=client.path).returncode)

        if args.install_client:
            exit_if_failed(client.exec_container_script("install_client.sh", args=[plugin]).returncode)


def pulpcore_manager(args, client):
    client.exec(["pulpcore-manager"] + args.command, interactive=True)


def profile(args, client):
    src_dir = client.config["SRC_DIR"]

    if args.action == "init":
        if args.plugin:
            profiles_dir = os.path.join(src_dir, args.plugin, "profiles")
            profile_name = f"{args.plugin}/{args.profile_name}"
        else:
            profiles_dir = os.path.join(client.path, "profiles")
            profile_name = args.profile_name

        new_profile_dir = os.path.join(profiles_dir, args.profile_name)

        pathlib.Path(profiles_dir).mkdir(exist_ok=True)

        try:
            pathlib.Path(new_profile_dir).mkdir(exist_ok=False)
        except FileExistsError:
            print(f"A profile already exists at {new_profile_dir}")
            exit_with_error(1)

        for template in profile_templates:
            with open(os.path.join(new_profile_dir, template["file"]), "x") as f:
                f.write(template["template"].format(profile_name=profile_name))

        print(f"New profile \"{profile_name}\" successfully created at: {new_profile_dir}")
        print(f"To use it set \"COMPOSE_PROFILE={profile_name}\"")

    elif args.action == "ls":
        plugins = []
        for f in os.listdir(src_dir):
            if os.path.isdir(os.path.join(src_dir, f)):
                plugins.append(f)
        
        for p in plugins:
            profile_dir = os.path.join(src_dir, p, "profiles")
            if not  os.path.isdir(profile_dir):
                continue

            print(f"Plugin: {p}")
            for f in os.listdir(profile_dir):
                if os.path.isdir(os.path.join(profile_dir, f)):
                    if p == "oci_env":
                        print(f"  {f}")
                    else:
                        print(f"  {p}/{f}")

    elif args.action == "docs":
        if "/" in args.profile:
            plugin, profile = args.profile.split("/", maxsplit=1)
        else:
            plugin = "oci_env"
            profile = args.profile

        profile_path = os.path.join(src_dir, plugin, "profiles", profile)
        if not os.path.isdir(profile_path):
            exit_with_error(f"{args.profile} doesn't exist")

        try:
            with open(os.path.join(profile_path, "README.md"), "r")as f:
                print(f.read())
        except FileNotFoundError:
            exit_with_error(f"{args.profile} doesn't have a README.md")