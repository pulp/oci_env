README_TEMPLATE = """
# {profile_name}

## Usage

*Add a description detailing what this profile does and any extra instructions for using it.*

## Extra Variables

*List any extra variables that user's can configure in their .compose.env*

- `MY_VAR_1`
    - Description: My custom variable.
    - Options:
        - 1: do thing 1.
        - 2: do thing 2.
    - Default: 1
- `MY_VAR_2`
    - Description: path to the file that does the thing.
    - Default: Unset
"""


INIT_SCRIPT_TEMPLATE = """
#!/bin/bash

# Add any scripts that need to run during startup here.

# PLEASE DELETE THIS FILE IF IT'S UNMODIFIED.
"""


COMPOSE_TEMPLATE = """
# Add any custom services for your profile here.

# PLEASE DELETE THIS FILE IF IT'S UNMODIFIED.

# version: "3.7"
#
# services:
#  my_custom_service:
#     image: foo:latest
"""


PULP_CONFIG_TEMPLATE = """
# Add any environment variables that this profile requires to run here.

# PLEASE DELETE THIS FILE IF IT'S UNMODIFIED.
"""


PROFILE_REQUIREMENTS_TEMPLATE = """
# List any profiles here that are required for this profile to run correctly.
# If a profile listed here is not in COMPOSE_PROFILE when this profile is loaded
# oci-env will exit.

# PLEASE DELETE THIS FILE IF IT'S UNMODIFIED.

# profile1
# profile2
"""


profile_templates = [
    {
        "file": "README.md",
        "template": README_TEMPLATE
    },
    {
        "file": "init.sh",
        "template": INIT_SCRIPT_TEMPLATE
    },
    {
        "file": "compose.yaml",
        "template": COMPOSE_TEMPLATE
    },
    {
        "file": "pulp_config.env",
        "template": PULP_CONFIG_TEMPLATE
    },
    {
        "file": "profile_requirements.txt",
        "template": PROFILE_REQUIREMENTS_TEMPLATE
    },
]
