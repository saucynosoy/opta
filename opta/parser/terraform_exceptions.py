import re

from opta.exceptions import TerraformError
from opta.utils import logger

ANSI_ESCAPE = re.compile(
    r"""
        \x1B  # ESC
        (?:   # 7-bit C1 Fe (except CSI)
            [@-Z\\-_]
        |     # or [ for CSI, followed by a control sequence
            \[
            [0-?]*  # Parameter bytes
            [ -/]*  # Intermediate bytes
            [@-~]   # Final byte
        )
    """,
    re.VERBOSE,
)


class TerraformErrorDetails:
    ERROR_START_POINT = "╷"
    ERROR_END_POINT = "╵"
    ERROR_BEGIN_POINT = "│"

    SIMPLER_MEANINGS = {
        "Error: Kubernetes cluster unreachable: the server has asked for the client to provide credentials": "Either the Credentials have expired, or Credentials do not have required permissions to access the Kubernetes cluster"
    }

    @classmethod
    def get_simplified_errors(cls, tf_error: TerraformError) -> tuple:
        indexed_simplified_errors: dict = {}
        indexed_detailed_errors: dict = {}
        index: int = 0
        if tf_error.stderr is None:
            return index, indexed_simplified_errors, indexed_detailed_errors

        ansi_escaped_error = ANSI_ESCAPE.sub("", tf_error.stderr.decode("UTF-8"))
        terraform_error_list = re.findall(r"╷(.*?)╵", ansi_escaped_error, flags=re.DOTALL)

        for terraform_error in terraform_error_list:
            split_tf_error = terraform_error.split(cls.ERROR_BEGIN_POINT)
            for error_line in split_tf_error:
                if "Error" in error_line:
                    indexed_simplified_errors[index] = cls.SIMPLER_MEANINGS.get(
                        error_line.strip(), error_line.strip()
                    )
                    indexed_detailed_errors[index] = terraform_error
                    index += 1
                    break

        return index, indexed_simplified_errors, indexed_detailed_errors


def parse_terraform_exceptions(error: TerraformError) -> None:
    (
        errors_count,
        simplified_errors,
        detailed_errors,
    ) = TerraformErrorDetails.get_simplified_errors(error)

    for error_index in range(0, errors_count):
        logger.info(
            f"\nSimplified Version:\t{simplified_errors[error_index]}"
            f"\nDetailed Version:\t{detailed_errors[error_index]}"
        )
