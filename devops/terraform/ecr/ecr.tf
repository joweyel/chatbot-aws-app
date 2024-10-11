data "aws_caller_identity" "current" {}

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
            "ecr:CompleteLayerUpload",
            "ecr:DescribeRepositories",
            "ecr:ListImages",
            "ecr:DescribeImages",
            "ecr:GetAuthorizationToken"
        ],
        "Resource": "arn:aws:ecr:${var.region}:${data.aws_caller_identity.current.account_id}:repository/cv-app-ecr-repo"
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

resource "aws_ecr_repository" "cv_app_ecr_repo" {
  name                 = var.ecr_repo_name
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