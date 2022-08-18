import subprocess
import os
from oci_env.utils import exit_if_failed

def compose(args, client):
    client.compose_command(args.command, interactive=True)


def exec(args, client):
    client.exec(args.command, interactive=True, service=args.service)


def db(args, client):
    if args.action == 'reset':
        exit_if_failed(
            client.exec_container_script(
                f"database_reset.sh",
                args=None,
                interactive=True)
        )
        client.compose_command(["restart"])
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
        print("Unsupported shell")
        exit(1)

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
