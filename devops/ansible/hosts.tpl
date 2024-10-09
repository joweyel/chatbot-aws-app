[jenkins-server]
${jenkins_server_ip}
[jenkins-server:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=/opt/app_key.pem
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
[build-server]
${build_server_ip}
[build-server:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=/opt/app_key.pem
ansible_ssh_common_args='-o StrictHostKeyChecking=no'