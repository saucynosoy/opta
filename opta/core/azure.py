from typing import TYPE_CHECKING, Any, List, Optional

from azure.identity import DefaultAzureCredential

from opta.exceptions import UserErrors
from opta.nice_subprocess import nice_run
from opta.utils import is_tool

if TYPE_CHECKING:
    from opta.layer import Layer


class Azure:
    project_id: Optional[str] = None

    def __init__(self, layer: "Layer"):
        self.layer = layer

    @classmethod
    def configure_kubectl(cls, providers: dict, outputs: dict) -> None:
        if not is_tool("az"):
            raise UserErrors("Please install az CLI first")

        rg_name = providers["terraform"]["backend"]["azurerm"]["resource_group_name"]
        cluster_name = outputs.get("k8s_cluster_name")

        if not cluster_name:
            raise Exception("The cluster name could not be determined.")

        nice_run(
            [
                "az",
                "aks",
                "get-credentials",
                "--resource-group",
                rg_name,
                "--name",
                cluster_name,
            ]
        )

    @classmethod
    def get_credentials(cls) -> Any:
        return DefaultAzureCredential()

    @classmethod
    def using_service_account(cls) -> bool:
        pass

    @classmethod
    def get_service_account_key_path(cls) -> str:
        pass

    @classmethod
    def get_service_account_raw_credentials(cls) -> str:
        pass

    # Upload the current opta config to the state bucket, under opta_config/.
    def upload_opta_config(self, config_data: str) -> None:
        # TODO(ankur)
        pass
        # bucket = self.layer.state_storage()
        # config_path = f"opta_config/{self.layer.name}"
        # credentials = self.get_credentials()
        # gcs_client = storage.Client(project=project_id, credentials=credentials)
        # bucket_object = gcs_client.get_bucket(bucket)
        # blob = storage.Blob(config_path, bucket_object)
        # blob.upload_from_string(config_data)
        # logger.debug("Uploaded opta config to gcs")

    def delete_opta_config(self) -> None:
        pass

    def get_current_zones(self, max_number: int = 3) -> List[str]:
        pass
