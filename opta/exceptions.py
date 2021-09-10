from subprocess import CalledProcessError


class UserErrors(Exception):
    """These are errors caused by improper usage or configuration and thus not surfaced to sentry"""


class MissingState(UserErrors):
    """These are errors caused by trying to fetch a terraform state which did not exist remotely."""


class TerraformError(CalledProcessError):
    """These are errors caused from Terraform."""

    def __init__(self, error: CalledProcessError):
        super().__init__(error.returncode, error.cmd, error.output, error.stderr)
