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
    profile,
    poll,
    edit_env,
    pulp,
)

from oci_env.utils import (
    Compose
)


def get_parser():
    parser = argparse.ArgumentParser(description='Pulp OCI image developer environment.')
    parser.add_argument('-v', action='store_true', dest='is_verbose', help="Print extra debug information.")
    parser.add_argument('-e', type=str, default="", dest='env_file', help="Specify an environment file to use other than the default.")
    parser.set_defaults(no_init_client=False)

    subparsers = parser.add_subparsers()

    parse_compose_command(subparsers)
    parse_exec_command(subparsers)
    parse_db_command(subparsers)
    parse_shell_command(subparsers)
    parse_test_command(subparsers)
    parse_generate_client_command(subparsers)
    parse_pulpcore_manager_command(subparsers)
    parse_profile_command(subparsers)
    parse_poll_command(subparsers)
    parse_pulp_cli_command(subparsers)
    parse_edit_env(subparsers)

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
    parser.add_argument('action', nargs=1, choices=["reset"])
    # parser.add_argument('-f', type=str, default="db.backup", dest='restore_file', help='Back up the database to a specific file.')
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


def parse_profile_command(subparsers):
    parser = subparsers.add_parser('profile', help='View and manage OCI Env profiles.')

    sub = parser.add_subparsers()

    ls = sub.add_parser('ls', help="View profiles")
    ls.set_defaults(func=profile, action="ls")

    init = sub.add_parser('init', help="Create a new OCI Env profile.")
    init.add_argument('-p', type=str, dest='plugin', default="", help="Plugin to add the new profile to. If none is specified this will be added to oci_env/profiles.")
    init.add_argument('profile_name', nargs="?", help='Name of the profile.')
    init.set_defaults(func=profile, action="init")

    docs = sub.add_parser('docs', help="View profile documentation.")
    docs.add_argument('profile', nargs="?", help='Profile to view.')
    docs.set_defaults(func=profile, action="docs")

    parser.set_defaults(no_init_client=True)


def parse_poll_command(subparsers):
    parser = subparsers.add_parser('poll', help='Poll the status API until it comes up.')
    parser.add_argument('--attempts', type=int, dest='attempts', default=10, help="Number of attempts to make.")
    parser.add_argument('--wait', type=int, dest='wait', default=10, help="Time in seconds to wait between attempts.")
    parser.set_defaults(func=poll)


def parse_pulp_cli_command(subparsers):
    parser = subparsers.add_parser('pulp', help='Run pulp cli.')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to pass to pulp cli.')
    parser.set_defaults(func=pulp)


def parse_edit_env(subparsers):
    parser = subparsers.add_parser(
        'edit-env', 
        help=(
            'Edit your current environment file in vim. To change the default editor, set the '
            'EDITOR environment variable to the path for the binary of your choosing.'
        )
    )
    parser.set_defaults(func=edit_env, no_init_client=True)


def main():
    parser = get_parser()
    args = parser.parse_args()

    if "func" not in args:
        parser.print_help()
        exit()

    try:
        # Initializing the client generates the .compiled/ directory and performs a lot of
        # validation that's not necessary for some sub and may cause these commands to fail
        # when the user has an invalid environment file set up.
        if args.no_init_client:
            args.func(args)
        else:
            client = Compose(args.is_verbose, args.env_file)
            args.func(args, client)
    except KeyboardInterrupt:
        print()
        exit(1)
