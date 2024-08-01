from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='oci-env',
    version='1.0.0',
    entry_points={
        'console_scripts': ['oci-env=oci_env.main:main'],
    },
    install_requires=["requests"],
    packages=find_packages(exclude=["tests", "tests.*"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/newswangerd/oci-env',
    description='CLI for running OCI Env.'
)
