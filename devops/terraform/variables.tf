variable "region" {
  description = "Region"
  default     = "us-east-1"
}

variable "ecr_repo_name" {
  description = "ECR repo name"
  type        = string
  default     = "flaskgpt-app"
}