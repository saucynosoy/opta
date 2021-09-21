from typing import TYPE_CHECKING

from ruamel.yaml.compat import StringIO

from opta.exceptions import UserErrors
from opta.module_processors.base import ModuleProcessor
from opta.utils import logger, yaml

if TYPE_CHECKING:
    from opta.layer import Layer
    from opta.module import Module


class HelmChartProcessor(ModuleProcessor):
    def __init__(self, module: "Module", layer: "Layer"):
        if module.data["type"] != "helm-chart":
            raise Exception(
                f"The module {module.name} was expected to be of type k8s service"
            )
        super(HelmChartProcessor, self).__init__(module, layer)

    def process(self, module_idx: int) -> None:
        if "repository" in self.module.data and "chart_version" not in self.module.data:
            raise UserErrors(
                "If you specify a remote repository you must give a version."
            )
        values = self.module.data.get("values", {})
        if values:
            stream = StringIO()
            yaml.dump(values, stream)
            logger.debug(
                f"These are the values passed in from the opta yaml:\n{stream.getvalue()}"
            )
        super(HelmChartProcessor, self).process(module_idx)
