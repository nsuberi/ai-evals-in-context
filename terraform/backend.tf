terraform {
  backend "s3" {
    bucket         = "portfolio-portal-terraform-state"
    key            = "ai-evals/environments/prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}
