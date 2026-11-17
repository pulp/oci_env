import contextlib
import io
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from oci_env import main as cli
from oci_env.utils import Compose


class AgentSelectionTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.agent_dir = self.root / ".compiled" / "agent_review"
        self.agent_dir.mkdir(parents=True)
        self.overlay = self.agent_dir / "plugin_volumes_compose.yaml"
        self.overlay.write_text("services: {}")
        self.env_file = self.agent_dir / "compose.env"
        self.config = {
            "OCI_AGENT_ID": "review",
            "OCI_AGENT_VOLUME_OVERLAY": str(self.overlay),
            "COMPOSE_PROJECT_NAME": "agent_review",
            "SRC_DIR": str(self.agent_dir),
            "DEV_SOURCE_PATH": "pulpcore",
            "API_PORT": "5117",
        }
        self.write_config()
        (self.root / "base").mkdir()
        (self.root / "profiles").mkdir()
        (self.root / "base" / "pulp_config.env").write_text("API_PORT={API_PORT}")
        (self.root / "compose.env").write_text("COMPOSE_PROJECT_NAME=default_dev")
        self.enterContext(
            patch.dict(os.environ, {"OCI_ENV_PATH": str(self.root)}, clear=True)
        )
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))

    def write_config(self, **updates):
        self.config.update(updates)
        self.env_file.write_text(
            "".join(f"{key}={value}\n" for key, value in self.config.items())
        )

    def run_cli(self, command):
        with patch.object(sys, "argv", ["oci-env", *shlex.split(command)]):
            cli.main()

    def test_agent_selection_preserves_project_mounts_and_api_address(self):
        with patch.dict(
            os.environ,
            {
                "COMPOSE_PROJECT_NAME": "wrong_project",
                "SRC_DIR": "/wrong/source",
                "OCI_AGENT_VOLUME_OVERLAY": "/wrong/overlay",
                "API_PORT": "5999",
            },
        ):
            for selector in ["-a review", "--agent review", f"-e {self.env_file}"]:
                with (
                    self.subTest(selector=selector),
                    patch("oci_env.utils.subprocess.call", return_value=0) as call,
                ):
                    self.run_cli(f"{selector} compose up -d")
                    command = call.call_args.args[0]
                    self.assertEqual(
                        command[:3], ["podman-compose", "-p", "agent_review"]
                    )
                    self.assertEqual(
                        command[-4:], ["-f", str(self.overlay), "up", "-d"]
                    )
                    self.assertEqual(
                        (self.agent_dir / "combined.env").read_text(), "API_PORT=5117"
                    )
        self.assertFalse((self.root / ".compiled" / "default_dev").exists())

    def test_default_target_is_unchanged(self):
        with patch("oci_env.utils.subprocess.call", return_value=0) as call:
            self.run_cli("compose ps")
        command = call.call_args.args[0]
        self.assertEqual(command[:3], ["podman-compose", "-p", "default_dev"])
        self.assertNotIn(str(self.overlay), command)

    def test_invalid_agent_never_falls_back_to_default(self):
        for agent_id in ["missing", "../review"]:
            with (
                self.subTest(agent_id=agent_id),
                patch("oci_env.main.Compose") as compose,
            ):
                with self.assertRaises(SystemExit):
                    self.run_cli(f"-a {agent_id} compose down")
                compose.assert_not_called()

    def test_missing_overlay_stops_before_compiling(self):
        self.overlay.unlink()
        with patch("oci_env.utils.parse_profiles") as compile_profiles:
            with self.assertRaises(SystemExit):
                self.run_cli("-a review compose up -d")
            compile_profiles.assert_not_called()

    def test_compose_failures_propagate(self):
        with (
            patch("oci_env.utils.subprocess.call", return_value=17),
            self.assertRaises(SystemExit) as error,
        ):
            self.run_cli("-a review compose up -d")
        self.assertEqual(error.exception.code, 17)

    def test_test_command_preserves_plugin_selection_and_pytest_arguments(self):
        cases = [
            (
                "pulpcore",
                "-p pulpcore unit -- -p no:cacheprovider",
                ["pulpcore", "-p", "no:cacheprovider"],
            ),
            (
                "pulpcore:pulp_python",
                "-p pulp_python unit -- -k catalog",
                ["pulp_python", "-k", "catalog"],
            ),
        ]
        for plugins, arguments, expected in cases:
            self.write_config(DEV_SOURCE_PATH=plugins)
            with (
                self.subTest(plugins=plugins),
                patch.object(
                    Compose,
                    "exec_container_script",
                    side_effect=[subprocess.CompletedProcess([], 0), 0],
                ) as run,
            ):
                self.run_cli(f"-a review test {arguments}")
                self.assertEqual(
                    run.call_args_list[0].args, ("install_unit_requirements.sh",)
                )
                self.assertEqual(run.call_args_list[0].kwargs["args"], expected[:1])
                self.assertEqual(run.call_args_list[1].args, ("run_unit_tests.sh",))
                self.assertEqual(run.call_args_list[1].kwargs["args"], expected)

    def test_without_plugin_only_installs_requirements(self):
        for plugins in ["pulpcore", "pulpcore:pulp_python"]:
            self.write_config(DEV_SOURCE_PATH=plugins)
            with (
                self.subTest(plugins=plugins),
                patch.object(
                    Compose,
                    "exec_container_script",
                    return_value=subprocess.CompletedProcess([], 0),
                ) as run,
            ):
                self.run_cli("-a review test functional")
                self.assertEqual(run.call_count, len(plugins.split(":")))
                for invocation, plugin in zip(run.call_args_list, plugins.split(":")):
                    self.assertEqual(
                        invocation.args, ("install_functional_requirements.sh",)
                    )
                    self.assertEqual(invocation.kwargs["args"], [plugin])

    def test_missing_generator_copy_fails_before_container_access(self):
        with patch.object(Compose, "exec") as execute:
            with self.assertRaises(SystemExit):
                self.run_cli("-a review generate-client")
            execute.assert_not_called()
