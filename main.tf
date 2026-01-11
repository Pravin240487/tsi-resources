provider "aws" {
  region = var.region
}

module "graviton_ec2" {
  source = "./terraform_modules/ec2"

  instance_name         = var.instance_name
  subnet_id             = var.subnet_id
  vpc_id                = var.vpc_id
  iam_role_arn          = var.iam_role_arn
  instance_type         = var.instance_type
  security_group_name   = var.security_group_name
  instance_profile_name = var.instance_profile_name
  user_data             = var.user_data
}
