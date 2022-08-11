from gettext import install
import subprocess
import os

def compose(args, client):
    client.compose_command(args.command, interactive=True)


def db(args, client):
    pass


def shell(args, client):
    cmd = []
    if args.shell == "bash":
        cmd = ["bash"]
    elif args.shell == "python":
        cmd = ["pulpcore-manager", "shell"]
    # this one doesn't seem to work 
    elif args.shell == "db":
        cmd = ["pulpcore-manager", "dbshell"]
    else:
        print("Unsupported shell")
        exit(1)

    client.exec(cmd, interactive=True)


def test(args, client):
    if args.install_deps:
        test_script = f"/opt/scripts/install_{args.test}_requirements.sh"

        if args.plugin:
            client.exec(["bash", test_script, project])
        else:
            for project in client.config["DEV_SOURCE_PATH"].split(":"):
                client.exec(["bash", test_script, project])

    else:
        if not args.plugin:
            print("plugin is required.")
            exit(1)
        test_script = f"/opt/scripts/run_{args.test}_tests.sh"
        client.exec(["bash", test_script, args.plugin] + args.args, interactive=True)


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

    env = {**client.config, "API_ROOT": api_root}

    for plugin in plugins:
        cmd = base_cmd + [plugin, ]
        if args.is_verbose:
            print(f"Running local command: {' '.join(cmd)}")

        subprocess.run(cmd, env=env)
        if args.install_client:
            client.exec(["bash", "/opt/scripts/install_client.sh", plugin])
