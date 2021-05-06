resource "azurerm_kubernetes_cluster" "main" {
  name                = "opta-${var.layer_name}"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  dns_prefix          = "opta"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
    enable_auto_scaling = true
    max_count = var.max_nodes
    min_count = var.min_nodes
  }

  identity {
    type = "SystemAssigned"
  }

  lifecycle {
    ignore_changes = [
      default_node_pool["node_count"]
    ]
  }
}
