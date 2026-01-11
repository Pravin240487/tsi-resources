terraform {
  backend "s3" {
    bucket         = "tf-state-bucket-110126"
    key            = "graviton_ec2/ec2.tfstate"
    region         = "ap-southeast-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
