
locals {
    env       = terraform.workspace == "Default" ? "SANDBOX" : upper(element(split("-", terraform.workspace), 0))
    namespace = lower(local.env)
    common_tags = {
      environment = "prod"
  }
}
