provider "aws" {
  region = var.region
}

# resource "aws_instance" "servers" {
#   ami           = "ami-0e86e20dae9224db8" # Ubuntu 24.04
#   key_name      = "app_key"

#   vpc_security_group_ids = [aws_security_group.app-sg.id]
#   subnet_id              = aws_subnet.app-public-subnet-01.id
#   for_each               = toset(["jenkins-server", "build-server", "ansible"])
#   # Only giving the build-server more resources
#   instance_type = each.key == "build-server" ? "t3.small" : "t2.micro"
#   tags = {
#     Name = "${each.key}"
#   }
# }

# Create ansible hosts files dynamically
data "template_file" "hosts_file" {
  template = file("${path.module}/../ansible/hosts.tpl")
  vars = {
    build_server_ip   = aws_instance.build-server.private_ip
    jenkins_server_ip = aws_instance.jenkins-server.private_ip
  }
}

resource "aws_instance" "jenkins-server" {
  ami           = "ami-005fc0f236362e99f" # Ubuntu 22.04
  instance_type = "t2.micro"
  key_name      = "app_key"

  vpc_security_group_ids = [aws_security_group.app-sg.id]
  subnet_id              = aws_subnet.app-public-subnet-01.id

  tags = {
    Name = "jenkins-server"
  }
}

resource "aws_instance" "build-server" {
  ami           = "ami-005fc0f236362e99f" # Ubuntu 22.04
  instance_type = "t3.small"
  key_name      = "app_key"

  vpc_security_group_ids = [aws_security_group.app-sg.id]
  subnet_id              = aws_subnet.app-public-subnet-01.id

  iam_instance_profile = module.ecr.ecr_instance_profile_name


  tags = {
    Name = "build-server"
  }
}

resource "aws_instance" "ansible" {
  ami           = "ami-005fc0f236362e99f" # Ubuntu 22.04
  instance_type = "t2.micro"
  key_name      = "app_key"

  vpc_security_group_ids = [aws_security_group.app-sg.id]
  subnet_id              = aws_subnet.app-public-subnet-01.id

  tags = {
    Name = "ansible"
  }

  # Required for ansible setup
  depends_on = [
    aws_instance.jenkins-server,
    aws_instance.build-server
  ]

  connection {
    type        = "ssh"
    user        = "ubuntu" # for Ubuntu instances
    private_key = file("app_key.pem")
    host        = self.public_ip
  }

  # Copy the SSH key to the home directory first
  provisioner "file" {
    source      = "app_key.pem"
    destination = "/home/ubuntu/app_key.pem" # Copy to home directory
  }

  # Copy the dynamically generated Ansible hosts file
  provisioner "file" {
    content     = data.template_file.hosts_file.rendered
    destination = "/home/ubuntu/hosts" # Copy to home directory
  }

  # Copy Ansible playbooks
  provisioner "file" {
    source      = "../ansible/jenkins-server-setup.yaml"
    destination = "/home/ubuntu/jenkins-server-setup.yaml" # Copy to home directory
  }
  provisioner "file" {
    source      = "../ansible/build-server-setup.yaml"
    destination = "/home/ubuntu/build-server-setup.yaml" # Copy to home directory
  }

  # Move files to /opt and set permissions
  provisioner "remote-exec" {
    inline = [
      "sudo mv /home/ubuntu/app_key.pem /opt/app_key.pem",                             # Move to /opt with sudo
      "sudo chmod 400 /opt/app_key.pem",                                               # Set permissions for the key
      "sudo mv /home/ubuntu/hosts /opt/hosts",                                         # Move hosts file
      "sudo mv /home/ubuntu/jenkins-server-setup.yaml /opt/jenkins-server-setup.yaml", # Move playbook
      "sudo mv /home/ubuntu/build-server-setup.yaml /opt/build-server-setup.yaml",     # Move playbook
      "sudo apt update",
      "sudo apt install -y software-properties-common",
      "sudo add-apt-repository -y --update ppa:ansible/ansible",
      "sudo apt install -y ansible"
    ]
  }

  # Execute Ansible playbooks
  provisioner "remote-exec" {
    inline = [
      "ansible-playbook -i /opt/hosts /opt/jenkins-server-setup.yaml",
      "ansible-playbook -i /opt/hosts /opt/build-server-setup.yaml",
    ]
  }
}


resource "aws_security_group" "app-sg" {
  name        = "app-sg"
  description = "Security Group of accessing resources"
  vpc_id      = aws_vpc.app-vpc.id

  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Jenkins access"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Streamlit access"
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
  tags = {
    Name = "port access"
  }
}

resource "aws_vpc" "app-vpc" {
  cidr_block = "10.1.0.0/16"
  tags = {
    Name = "app-vpc"
  }
}

resource "aws_subnet" "app-public-subnet-01" {
  vpc_id                  = aws_vpc.app-vpc.id
  cidr_block              = "10.1.1.0/24"
  map_public_ip_on_launch = "true"
  availability_zone       = "us-east-1a"
  tags = {
    Name = "app-public-subnet-01"
  }
}

resource "aws_subnet" "app-public-subnet-02" {
  vpc_id                  = aws_vpc.app-vpc.id
  cidr_block              = "10.1.2.0/24"
  map_public_ip_on_launch = "true"
  availability_zone       = "us-east-1b"
  tags = {
    Name = "app-public-subnet-02"
  }
}

resource "aws_internet_gateway" "app-igw" {
  vpc_id = aws_vpc.app-vpc.id
  tags = {
    Name = "app-igw"
  }
}

resource "aws_route_table" "app-public-rt" {
  vpc_id = aws_vpc.app-vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.app-igw.id
  }
}

resource "aws_route_table_association" "app-rta-public-subnet-01" {
  subnet_id      = aws_subnet.app-public-subnet-01.id
  route_table_id = aws_route_table.app-public-rt.id
}

resource "aws_route_table_association" "app-rta-public-subnet-02" {
  subnet_id      = aws_subnet.app-public-subnet-02.id
  route_table_id = aws_route_table.app-public-rt.id
}

module "ecr" {
  source        = "./ecr"
  ecr_repo_name = var.ecr_repo_name
  region        = var.region
}

module "sgs" {
  source = "./sg_eks"
  vpc_id = aws_vpc.app-vpc.id
}

module "eks" {
  source     = "./eks"
  vpc_id     = aws_vpc.app-vpc.id
  subnet_ids = [aws_subnet.app-public-subnet-01.id, aws_subnet.app-public-subnet-02.id]
  sg_ids     = module.sgs.security_group_public
}