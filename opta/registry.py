import os
import shutil
from typing import Any, Dict, List

from ruamel.yaml import YAML

yaml = YAML(
    typ="safe"
)  # Duplicate because constants can't import utils and yaml really is a util

SERVICE_MODULE_INDEX = """---
title: "Service"
linkTitle: "Service"
weight: 1
description: This section provides the list of module types for the user to use in a service Opta yaml for this cloud, along with their inputs and outputs.
---
"""

ENVIRONMENT_MODULE_INDEX = """---
title: "Environment"
linkTitle: "Environment"
weight: 1
description: This section provides the list of module types for the user to use in a environment Opta yaml for this cloud, along with their inputs and outputs.
---
"""


def make_registry_dict() -> Dict[Any, Any]:
    registry_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config", "registry"
    )
    registry_dict: Dict[Any, Any] = yaml.load(
        open(os.path.join(registry_path, "index.yaml"))
    )
    common_modules_path = os.path.join(registry_path, "common", "modules")
    with open(os.path.join(registry_path, "index.md"), "r") as f:
        registry_dict["text"] = f.read()
    for cloud in ["aws", "azurerm", "google", "local"]:
        cloud_path = os.path.join(registry_path, cloud)
        cloud_dict = yaml.load(open(os.path.join(cloud_path, "index.yaml")))
        cloud_dict["modules"] = {}
        with open(os.path.join(cloud_path, "index.md"), "r") as f:
            cloud_dict["text"] = f.read()
        module_path = os.path.join(cloud_path, "modules")
        cloud_dict["modules"] = {
            **_make_module_registry_dict(module_path),
            **_make_module_registry_dict(common_modules_path),
        }
        registry_dict[cloud] = cloud_dict

    return registry_dict


INPUTS_TABLE_HEADING = """
| Name      | Description | Default | Required |
| ----------- | ----------- | ------- | -------- |
"""

OUTPUTS_TABLE_HEADING = """
| Name      | Description |
| ----------- | ----------- |
"""


def _make_module_docs(vanilla_text: str, module_dict: Dict[Any, Any]) -> str:
    input_lines: List[str] = []
    output_lines: List[str] = []
    inputs: Dict[str, Any]
    for inputs in module_dict["inputs"]:
        if not inputs["user_facing"]:
            continue
        name = inputs["name"]
        default = inputs["default"]
        description = inputs["description"].replace("\n", " ")
        required = "required=True" in inputs["validator"]
        table_row = f"| `{name}` | {description} | `{default}` | {required} |"
        input_lines.append(table_row)

    output: Dict[str, Any]
    for output in module_dict["outputs"]:
        if not output["export"]:
            continue
        name = output["name"]
        description = output["description"].replace("\n", " ")
        table_row = f"| `{name}` | {description} |"
        output_lines.append(table_row)

    result = f"{vanilla_text}\n\n"
    if len(input_lines) > 0:
        result += "## Fields\n\n"
        result += INPUTS_TABLE_HEADING + "\n".join(input_lines)
    if len(output_lines) > 0:
        result += "\n\n## Outputs\n\n"
        result += OUTPUTS_TABLE_HEADING + "\n".join(output_lines)
    return result


def _make_module_registry_dict(directory: str) -> Dict[Any, Any]:
    if not os.path.exists(directory):
        raise Exception(f"Non-existing directory given as input: {directory}")
    module_names = [
        f.split(".")[0]
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and f.endswith("yaml")
    ]
    modules_dict = {}
    for module_name in module_names:
        module_dict = yaml.load(open(os.path.join(directory, f"{module_name}.yaml")))
        with open(os.path.join(directory, f"{module_name}.md"), "r") as f:
            module_dict["text"] = _make_module_docs(f.read(), module_dict)
        for input in module_dict["inputs"]:
            input["required"] = (
                input["user_facing"] and "required=True" in input["validator"]
            )
        module_dict["validators"] = _make_module_validators(module_dict)
        modules_dict[module_name] = module_dict
    return modules_dict


def _make_module_validators(module_dict: Dict) -> List[Dict]:
    main_validator: Dict[Any, Any] = {
        "type": "str(required=True)",
        "name": "str(required=False)",
    }
    for input in module_dict["inputs"]:
        if not input["user_facing"]:
            continue
        main_validator[input["name"]] = input["validator"]

    validator_list = [main_validator]
    if module_dict.get("extra_validators"):
        validator_list.append(module_dict["extra_validators"])
    return validator_list


def make_registry_docs(directory: str) -> None:
    if not os.path.exists(directory):
        raise Exception(f"Non-existing directory given as input: {directory}")
    registry_dict = make_registry_dict()
    base_path = os.path.join(directory, "Reference")
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path)
    with open(os.path.join(base_path, "_index.md"), "w") as f:
        f.write(registry_dict["text"])
    for cloud in ["aws", "google", "azurerm"]:
        cloud_path = os.path.join(base_path, cloud)
        os.makedirs(cloud_path)
        cloud_dict = registry_dict[cloud]
        with open(os.path.join(cloud_path, "_index.md"), "w") as f:
            f.write(cloud_dict["text"])
        environment_module_path = os.path.join(cloud_path, "environment_modules")
        os.makedirs(environment_module_path)
        with open(os.path.join(environment_module_path, "_index.md"), "w") as f:
            f.write(ENVIRONMENT_MODULE_INDEX)
        service_module_path = os.path.join(cloud_path, "service_modules")
        os.makedirs(service_module_path)
        with open(os.path.join(service_module_path, "_index.md"), "w") as f:
            f.write(SERVICE_MODULE_INDEX)
        for module_name, module_dict in cloud_dict["modules"].items():
            module_path = (
                environment_module_path
                if module_dict["environment_module"]
                else service_module_path
            )
            with open(os.path.join(module_path, f"{module_name}.md"), "w") as f:
                f.write(module_dict["text"])
