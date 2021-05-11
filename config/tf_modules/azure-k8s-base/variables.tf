locals {
  target_ports = var.delegated ? { http: "http", https: "http" } : { http: "http" }
  container_ports = var.delegated ? { http: 80, https: 443 } : { http: 80, https: 443 }
  config = { ssl-redirect: false }
}

data "azurerm_resource_group" "main" {
  name = "optarunxstaging77"
}

variable "delegated" {
  type = bool
  default = false
}

variable "cert_arn" {
  type = string
  default = ""
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
