data "azurerm_resource_group" "main" {
  name = "optarunxstaging77"
}

variable "env_name" {
  description = "Env name"
  type = string
}

variable "layer_name" {
  description = "Layer name"
  type        = string
}

variable "module_name" {
  description = "Module name"
  type = string
}

variable "max_nodes" {
  type    = number
  default = 5
}

variable "min_nodes" {
  type    = number
  default = 1
}


variable "node_disk_size" {
  type    = number
  default = 20
}

variable "node_instance_type" {
  type    = string
  default = "n2-highcpu-4"
}
