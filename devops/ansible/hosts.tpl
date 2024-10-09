[jenkins-server]
{{ jenkins_server_ip }}
[jenkins-server:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=/opt/app_key.pem
[build-slave]
{{ build_server_ip }}
[build-server:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=/opt/app_key.pem