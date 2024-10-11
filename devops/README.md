# Integrating the app into a CI-CD pipeline hosted on AWS

## AWS setup

### Getting AWS credentials
- <u>Create IAM user</u>
  - **User name**: `cv_app_user`
  - **Attach policies directly**: `AdministratorAccess` (can be changed later)
- <u>Generate Access keys</u>
  - **Use case**: `Command Line Interface (CLI)`
  - **Tag**: `terraform credentials`
  - Download the credentials and save them securely
- Configuring `awscli`
  ```bash
  # Option 1: With awscli
  aws configure --profile cv_app_user # set the credentials here

  # Option 2: With environment variables
  export AWS_PROFILE=cv_app_user
  export AWS_ACCESS_KEY_ID=...
  export AWS_SECRET_ACCESS_KEY=...
  export AWS_DEFAULT_REGION=...
  ```
- Check connection with AWS
  ```bash
  aws s3 ls
  ```
- <u>Generate EC2 key-pair</u>
  - **Name**: `app_key`
  - **Key pair type**: `RSA`
  - **Private key file format**: `.pem`
  - Download the key and place it in `~/.ssh/`
  - Change permissions: `chmod 400 ~/.ssh/app_key.pem`
  - Copy the key to the [terraform](./devops/terraform/)-directory: `cp ~/.ssh/app_key.pem devops/terraform/`

### Creating AWS infrastructure with Terraform
To create the required cloud infrastructure terraform is used. This creates a vpc with three EC2 instances
- ansible
- jenkins-server
- build-server
- ECR
- EKS

The application of Ansible playbooks is already automated within terraform and you can therefore directly use the jenkins-server when the provisioning is done. The main terraform file is [main.tf](./terraform/main.tf)

To create the ressources, run the following commands:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Jenkins setup
1. At the initial login you will be prompted to obtain the login password from here:
   ```bash
   sudo cat /var/lib/jenkins/secrets/initialAdminPassword
   ```
   You can use this to login to jenkins but you can also change it later
2. After login: Select `Install suggested plugins`
3. `Create your admin user` where you set your username and password
4. Finish the `Instance Configuration` by clicking **Save and Finish**


### Installing required plugins
Go to `[Dashboard]` -> `[Manage Jenkins]` -> `[Plugins]` -> `[Available plugins]`
<!-- - Multibranch Scan Webhook Trigger -->
<!-- - Artifactory -->
<!-- - SonarQube Scanner -->
- AWS Credentials
- GitHub Integration Plugin
- Docker Pipeline

### Set up build node

1. Add ssh credentials to Jenkins
2. Add node

#### Create credentials to connect to build server
- Go to `[Dashboard]` -> `[Manage Jenkins]` -> `[Credentials]` -> `[System]` -> `[Global credentials (unrestricted)]` and add:
    - **Kind**: `SSH Username with private key`
    - **Scope**: `Global`
    - **ID**: `build-server-cred`
    - **Description**: `build server credentials`
    - **Username**: `ubuntu`
    - **Private key**: content of `app_key.pem` 


#### Use build server as node
- Go to `[Dashboard]` -> `[Manage Jenkins]` -> `[Nodes]` -> `[New Node]`
- **New node**:
  - **Node name**: python-build
  - **Type**: Permanent Agent
  - <u>Use this information to configure the node</u>:
      - **Number of executors**: 2
      - **Remote root directory**: `/home/ubuntu/jenkins`
      - **Labels**: `python`
      - **Usage**: Use this node as much as possible
      - **Launch method**: `Launch agents via SSH`
      - **Host**: `Private_IP_of_Slave`
      - **Credentials**: `Jenkins_Slave_Credentials`
      - **Host Key Verification Strategy**: Non verifying Verification Strategy
      - **Availability**: Keep this agent online as much as possible

### Create Pipeline
- Go to `[Dashboard]` -> `[All]` -> `[New Item]`
- <u>Create Item with these properties:</u>
    - Item name: `cv_app_pipeline`
    - Item type: `pipeline`
- <u>Check the following:</u>
  - GitHub hook trigger for GITScm polling
- <u>Set `Pipeline`-parameter as following</u>:
  - **Definition**: `Pipeline script from SCM`
    - **SCM**: `Git`
      - **Repositories**: 
        - **Repository URL**: https://github.com/joweyel/face-landmark-app
        - **Credentials**: `-none-` (not required for public repo)
      - **Branches to build**:
        - **Branch Specifier**: `*/main`

### Adding GitHub credentials to Jenkins
Generate a `Personal access tokens (classic)` on Github in the settings [here](https://github.com/settings/tokens) and name it `jenkins-token`

Set the parameters as follows:
- Expiration: 30 days
- Check all privileges
- Obtain the git token
  
<u>In Jenkins GUI</u>:
- `[Dashboard]` -> `[Manage Jenkins]` -> `[Credentials]` -> `[System]` -> `[Global credentials]` -> `[Add credentials]`
- **Add New credentials**
  - **Kind**: Username with password
  - **Scope**: Global
  - **Username**: <your_git_username>
  - **Password**: <git_token>
  - **ID**: Github_Cred

### Add Webhook to Github
- Go to settings of your forked `face-landmark-app` repo here: https://github.com/your_user/face-landmark-app/settings/hooks/
  - **Payload URL**: `http://JENKINS_PUBLIC_IP:8080/github-webhook/`
  - **Content type**: `application/json`
  - **SSL verification**:
    - Enable SSL verification
  - **Trigger Webhook at**: 
    - Just the push event

The pipeline should now be able to be triggered with every `git push` command.

### Connecting Jenkinsfile with AWS resources

- <u><b>Setting AWS-Credentials</b></u>
  - Go to `[Dashboard]` -> `[Manage Jenkins]` -> `[Credentials]` -> `[System]` -> `[Global credentials (unrestricted)]` -> `[+ Add Credentials]` and choose the following settings
  - **Kind**: `AWS Credentials`
    - **Scope**: `Global`
    - **ID**: `cv_app_user-aws-creds`
    - **Description**: `cv_app_user-aws-creds`
    - **Access Key ID**: `<AWS_ACCESS_KEY_ID>`
    - **Secret Access Key**: `<AWS_SECRET_ACCESS_KEY>`
  
  The AWS credentials can now be set by using the following code inside steps of a stage:
  ```groovy
    withCredentials([aws(accessKeyVariable: 'AWS_ACCESS_KEY_ID', credentialsId: 'cv_app_user-aws-creds', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {
        ...
    }
  ```

- <u><b>Setting AWS region / profile & ECR Registry URL as credentials</b></u>
  - Setting them as credentials avoids putting sensitive information in the [Jenkinsfile](./jenkins/Jenkinsfile)
  - Go to `[Dashboard]` -> `[Manage Jenkins]` -> `[Credentials]` -> `[System]` -> `[Global credentials (unrestricted)]` -> `[+ Add Credentials]` and choose the following settings
  - For `AWS_REGION`:
    - **Kind**: `Secret test`
      - **Scope**: `General`
      - **Secret**: `us-east-1`  (where everything is done)
      - **ID**: `aws_region`
  - For `AWS_PROFILE`:
    - **Kind**: `Secret test`
      - **Scope**: `General`
      - **Secret**: `cv_app_user`  (where everything is done)
      - **ID**: `aws_profile`
  - For `ECR_REGISTRY` (find the URI of *`cv-app-ecr-repo`* in the ECR section of AWS)
    - **Kind**: `Secret test`
      - **Scope**: `General`
      - **Secret**: `<user-id>.dkr.ecr.<aws-region>.amazonaws.com/`  (example)
      - **ID**: `ecr_registry_url`
  
