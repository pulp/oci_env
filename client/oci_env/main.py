import argparse
import os

from oci_env.agent import agent_dispatch, load_agent_env
from oci_env.commands import (
    compose,
    db,
    exec,
    generate_client,
    phelper,
    poll,
    profile,
    pulpcore_manager,
    shell,
    test,
)
from oci_env.utils import (
    Compose,
    get_oci_env_path,
)


def get_env_bool(key, default=False):
    if key not in os.environ:
        return default

    val = os.environ.get(key)
    if val is None:
        return False

    # truthy
    if val.lower().strip() in ['yes', 'true', '1']:
        return True

    # falsy
    if val.lower().strip() in ['no', 'false', '0', 'null', 'none', '']:
        return False

    return default


def get_parser():
    parser = argparse.ArgumentParser(description='Pulp OCI image developer environment.')
    parser.add_argument('-v', action='store_true', dest='is_verbose', default=get_env_bool("OCI_VERBOSE"), help="Print extra debug information.")
    target = parser.add_mutually_exclusive_group()
    target.add_argument('-e', type=str, default="", dest='env_file', help="Specify an environment file to use other than the default.")
    target.add_argument('-a', '--agent', dest='target_agent', metavar='AGENT_ID', help="Run the command against an existing agent environment.")

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
    parse_phelper_commands(subparsers)
    parse_agent_command(subparsers)

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
    parser.add_argument('action', nargs=1, choices=["reset", "snapshot", "restore"])
    parser.add_argument(
        '-f',
        type=str,
        default="pulp_backup",
        dest='filename',
        help=('Back up or restore the database and artifacts to a file in OCI_ENV_PATH/db_backup/')
    )
    parser.add_argument(
        '--migrate',
        action="store_true",
        dest='migrate',
        help=('Run migrations after restoring the databse.')
    )
    parser.set_defaults(func=db)


def parse_shell_command(subparsers):
    parser = subparsers.add_parser('shell', help='Launch an interactive shell.')
    parser.add_argument('shell', nargs="?", default="bash", choices=["bash", "python", "db"])
    parser.add_argument("--privileged", action="store_true", dest="privileged")
    parser.set_defaults(func=shell)


def parse_test_command(subparsers):
    parser = subparsers.add_parser('test', help='Run tests and install requirements.')
    parser.add_argument('test', choices=["functional", "unit", "lint", "performance"])
    parser.add_argument('-i', action='store_true', dest='install_deps', help="Deprecated no-op. Test dependencies are always installed.")
    parser.add_argument('-p', type=str, default="", dest='plugin', help="Plugin to test; place before the suite. Defaults to the sole source plugin in an agent environment.")
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments to pass to pytest. Use -k/-m to select tests (file paths are not supported with --pyargs).')
    parser.add_argument("--privileged", action="store_true", dest="privileged")
    parser.set_defaults(func=test)


def parse_generate_client_command(subparsers):
    parser = subparsers.add_parser('generate-client', help='Generate the the pulp client.')
    parser.add_argument('plugin', nargs="?", default=None, help="Plugin to generate a client for. If no plugin is specified clients will be generated for all plugins in DEV_SOURCE_PATH.")
    parser.add_argument('-l', '--language', default="python", choices=['python', 'ruby'], help="Language to generate a client for. If no language is specified clients will be generated for python.")
    parser.add_argument('-i', action='store_true', dest='install_client', help="Deprecated no-op. Python clients are always installed after generating.")
    parser.add_argument('-v', '--api-version', default="v3", choices=['v3', 'v4'], dest='api_version', help="API-version to generate the clients for.")

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


def parse_poll_command(subparsers):
    parser = subparsers.add_parser('poll', help='Poll the status API until it comes up.')
    parser.add_argument('--attempts', type=int, dest='attempts', default=10, help="Number of attempts to make.")
    parser.add_argument('--wait', type=int, dest='wait', default=10, help="Time in seconds to wait between attempts.")
    parser.set_defaults(func=poll)


def parse_phelper_commands(subparsers):
    for action in ("start", "stop", "restart"):
        parser = subparsers.add_parser(f'p{action}', help=f'{action.capitalize()} all/any Pulp service')
        parser.add_argument('services', nargs=argparse.REMAINDER, help=f'List of services to {action}, leave blank to {action} all')
        parser.set_defaults(func=phelper, action=action)
    parser = subparsers.add_parser('phelp', help='Show available pcommands available in the container.')
    parser.set_defaults(func=phelper, action="help")
    parser = subparsers.add_parser('pstatus', help='Return the status of pulp-related services.')
    parser.set_defaults(func=phelper, action="status")
    parser = subparsers.add_parser('pclean', help='Restore Pulp to a clean install state.')
    parser.set_defaults(func=phelper, action="clean")
    parser = subparsers.add_parser('pdbreset', help='Reset the Pulp database.')
    parser.set_defaults(func=phelper, action="dbreset")


def parse_agent_command(subparsers):
    parser = subparsers.add_parser(
        "agent",
        help="Create and manage lean isolated environments for parallel agent work.",
    )
    agent_sub = parser.add_subparsers(dest="agent_action", required=True)

    create = agent_sub.add_parser("create", help="Allocate a lean agent environment.")
    create.add_argument("agent_id", help="Unique agent id (used in project name and env file).")
    create.add_argument(
        "--plugins",
        default="pulpcore",
        help=(
            "Colon-separated PLUGIN[=PATH] entries for DEV_SOURCE_PATH (default: pulpcore). "
            "PATH may be a Cursor worktree or any plugin checkout; omit PATH to use "
            "<host-src-dir>/<plugin>."
        ),
    )
    create.add_argument(
        "--host-src-dir",
        default=None,
        help=(
            "Host directory used to resolve plugins listed without an explicit path "
            "(default: SRC_DIR from compose.env or parent of oci_env)."
        ),
    )
    create.add_argument("--port", type=int, default=None, help="API port (default: allocate from 5100-5199).")
    create.add_argument(
        "--env",
        action="append",
        default=[],
        dest="env_vars",
        metavar="KEY=VALUE",
        help=(
            "Set a variable in the agent env file (repeatable). "
            "Examples: --env COMPOSE_PROFILE=lean:local_fixtures --env LEAN_MEM_LIMIT=1g."
        ),
    )
    create.set_defaults(func=agent_dispatch, agent_action="create")

    ls = agent_sub.add_parser("ls", help="List agent environments.")
    ls.set_defaults(func=agent_dispatch, agent_action="ls")

    destroy = agent_sub.add_parser("destroy", help="Stop an agent environment and remove volumes/env.")
    destroy.add_argument("agent_id", help="Agent id to destroy.")
    destroy.set_defaults(func=agent_dispatch, agent_action="destroy")


def main():
    parser = get_parser()
    args = parser.parse_args()

    if "func" not in args:
        parser.print_help()
        exit()

    # Agent management handles its own env files and must not require compose.env.
    if getattr(args, "func", None) is agent_dispatch:
        if args.target_agent is not None or args.env_file:
            parser.error("-a/--agent and -e select a target for operational commands, not agent management")
        try:
            args.func(args)
        except KeyboardInterrupt:
            print()
            exit(1)
        return

    env_file = args.env_file
    if args.target_agent is not None:
        env_file, _ = load_agent_env(get_oci_env_path(args.is_verbose), args.target_agent)

    client = Compose(args.is_verbose, env_file)
    try:
        args.func(args, client)
    except KeyboardInterrupt:
        print()
        exit(1)


if __name__ == "__main__":
    main()
