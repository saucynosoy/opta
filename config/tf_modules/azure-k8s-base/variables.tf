data "azurerm_resource_group" "main" {
  name = "opta-${var.layer_name}"
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

variable "domain" {
  type = string
  default = ""
}

variable "high_availability" {
  type = bool
  default = true
}
