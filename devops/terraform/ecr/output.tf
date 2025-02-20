output "repository_url" {
  value = aws_ecr_repository.cv_app_ecr_repo.repository_url
}

output "repository_arn" {
  value = aws_ecr_repository.cv_app_ecr_repo.arn
}

output "ecr_instance_profile_name" {
  value = aws_iam_instance_profile.ecr_instance_profile.name
}