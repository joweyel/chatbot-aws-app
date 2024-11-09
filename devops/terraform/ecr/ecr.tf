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
        "Resource": "arn:aws:ecr:${var.region}:${data.aws_caller_identity.current.account_id}:repository/flaskgpt-app"
      }
    ]
  }
  EOF
}

resource "aws_s3_bucket" "eb-bucket" {
  bucket = "eb-dockerrun-bucket"
  tags = {
    Name = "eb-dockerrun-bucket"
  }
}

resource "aws_iam_policy" "s3_access_policy" {
  name        = "s3_access_policy"
  description = "Allow access to S3 Bucket"

  policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:Get*",
          "s3:Put*",
          "s3:List*"
        ],
        "Resource": [
          "arn:aws:s3:::${aws_s3_bucket.eb-bucket.bucket}",
          "arn:aws:s3:::${aws_s3_bucket.eb-bucket.bucket}/*"
        ]
      }
    ]
  }
  EOF
}

# Attach ECR access
resource "aws_iam_role_policy_attachment" "ecr_policy_attachment" {
  role       = aws_iam_role.ecr_access_role.name
  policy_arn = aws_iam_policy.ecr_access_policy.arn
}

# Attach S3 access
resource "aws_iam_role_policy_attachment" "s3_policy_attachment" {
  role       = aws_iam_role.ecr_access_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
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
    aws_iam_role_policy_attachment.ecr_policy_attachment
  ]

  tags = {
    Name = var.ecr_repo_name
  }
}