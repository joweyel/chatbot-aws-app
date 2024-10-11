resource "aws_iam_role" "ecr_access_role" {
  name = "ecr-access-role"
  
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ec2.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  EOF
}

resource "aws_iam_policy" "ecr_access_policy" {
  name        = "ecr_access_policy"
  description = "Policy to access ECR"

  policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ],
        "Resource": "*"
      }
    ]
  }
  EOF
}

resource "aws_iam_role_policy_attachment" "ECSAccessEC2Policy" {
  role       = aws_iam_role.ecr_access_role.name
  policy_arn = aws_iam_policy.ecr_access_policy.arn
}

resource "aws_iam_instance_profile" "ecr_instance_profile" {
  name = "ecr_instance_profile"
  role = aws_iam_role.ecr_access_role.name
}

# resource "aws_ecr_lifecycle_policy" "lifecycle_policy" {
#   repository = aws_ecr_repository.cv_app_ecr_repo.name
#   policy = <<EOF
#   {
#     "rules": [
#       {
#         "rulePriority": 1,
#         "description": "Expire untagged images older than 7 days",
#         "selection": {
#           "tagStatus": "untagged",
#           "countType": "sinceImagePushed",
#           "countUnit": "days",
#           "countNumber": 7
#         },
#         "action": {
#           "type": "expire"
#         }
#       },
#       {
#         "rulePriority": 2,
#         "description": "Expire tagged images older than 30 days",
#         "selection": {
#           "tagStatus": "tagged",
#           "countType": "sinceImagePushed",
#           "countUnit": "days",
#           "countNumber": 30
#         },
#         "action": {
#           "type": "expire"
#         }
#       }
#     ]
#   }
#   EOF

#   depends_on = [ 
#     aws_ecr_repository.cv_app_ecr_repo
#    ]
# }

resource "aws_ecr_repository" "cv_app_ecr_repo" {
  name = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }


  depends_on = [
    aws_iam_role_policy_attachment.ECSAccessEC2Policy
  ]

  tags = {
    Name = var.ecr_repo_name
  }
}
