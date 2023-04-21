import os
import subprocess

from django.conf import settings

projects = os.getenv("DEV_SOURCE_PATH").split(":")

# load django settings on the fly
settings.DYNACONF.configure()
api_root = settings.get("API_ROOT")


test_requirements_scripts = [
    "install_functional_requirements.sh",
    "install_performance_requirements.sh",
    "install_unit_requirements.sh",
    "install_lint_requirements.sh",
]

for project in projects:
    print(f"Installing test requirements for {project}...")
    for test_script in test_requirements_scripts:
        test_script = os.path.join("/opt/oci_env/base/container_scripts/", test_script)
        print(f"Running {test_script} for {project}...")

        try:
            subprocess.run(["bash", test_script, project], capture_output=False)
        except subprocess.CalledProcessError as err:
            print(test_script, project, err.stdout)
