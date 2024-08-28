provider "aws" {
  default_tags {
    tags = local.common_tags
  }
}
