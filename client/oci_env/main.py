import argparse
from distutils.command.config import config

from oci_env.commands import (
    compose,
    exec,
    db,
    shell,
    test,
    generate_client,
    pulpcore_manager,
)

from oci_env.utils import (
    Compose
)

def get_parser():
    parser = argparse.ArgumentParser(description='Pulp OCI image developer environment.')
    parser.add_argument('-v', action='store_true', dest='is_verbose', help="Print extra debug information.")

    subparsers = parser.add_subparsers()

    parse_compose_command(subparsers)
    parse_exec_command(subparsers)
    parse_db_command(subparsers)
    parse_shell_command(subparsers)
    parse_test_command(subparsers)
    parse_generate_client_command(subparsers)
    parse_pulpcore_manager_command(subparsers)

    return parser


def parse_compose_command(subparsers):
    parser = subparsers.add_parser('compose', help='Run any podman or docker-compose script.')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to pass to compose.')
    parser.set_defaults(func=compose)


def parse_exec_command(subparsers):
    parser = subparsers.add_parser('exec', help="Run a command using podman/docker exec. This bypasses docker/podman-compose.")
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to pass to the container.')
    parser.add_argument('-s', type=str, default=None, dest='service', help="Service to run the command on. This defaults to API_CONTAINER in your .compose.env, which is set to 'pulp' by default.")
    parser.set_defaults(func=exec)


def parse_db_command(subparsers):
     parser = subparsers.add_parser('db', help='Manage the application DB.')
     # parser.add_argument('action', nargs='?', choices=["reset", "snapshot", "restore"])
     parser.add_argument('action', nargs='?', choices=["reset"])
     parser.add_argument('-f', type=str, default="db.backup", dest='restore_file', help='Back up the database to a specific file.')
     parser.set_defaults(func=db)


def parse_shell_command(subparsers):
    parser = subparsers.add_parser('shell', help='Launch an interactive shell.')
    parser.add_argument('shell', nargs="?", default="bash", choices=["bash", "python", "db"])
    parser.set_defaults(func=shell)


def parse_test_command(subparsers):
    parser = subparsers.add_parser('test', help='Run tests and install requirements.')
    parser.add_argument('test', choices=["functional", "unit", "lint"])
    parser.add_argument('-i', action='store_true', dest='install_deps', help="Install the python dependencies for the selected test instead of running it. If -p is not specified this will install all the test dependencies for each plugin in DEV_SOURCE_PATH.")
    parser.add_argument('-p', type=str, default="", dest='plugin', help="Plugin to test. Tests won't run unless this is specified.")
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments to pass to pytest.')
    parser.set_defaults(func=test)


def parse_generate_client_command(subparsers):
    parser = subparsers.add_parser('generate-client', help='Generate the the pulp client.')
    parser.add_argument('plugin', nargs="?", default=None, help="Plugin to generate a client for. If no plugin is specified clients will be generated for all plugins in DEV_SOURCE_PATH.")
    parser.add_argument('-i', action='store_true', dest='install_client', help="Install the client after generating it.")

    parser.set_defaults(func=generate_client)


def parse_pulpcore_manager_command(subparsers):
    parser = subparsers.add_parser('pulpcore-manager', help='Run a pulpcore-manager command.')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to pass to pulpcore-manager.')
    parser.set_defaults(func=pulpcore_manager)


def main():
    parser = get_parser()
    args = parser.parse_args()

    if "func" not in args:
        parser.print_help()
        exit()

    client = Compose(args.is_verbose)
    try:
        args.func(args, client)
    except KeyboardInterrupt:
        print()
        exit(1)
