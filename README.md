This project automates the setup of a PostgreSQL primary-replica architecture on AWS. It leverages Terraform for infrastructure provisioning, Ansible for PostgreSQL configuration, and a Flask API to handle the orchestration.

Prerequisites:
To run this project, you need the following:

AWS Account: To deploy EC2 instances.
Terraform: For infrastructure provisioning.
Ansible: To configure PostgreSQL on instances.
Python 3 and the following libraries:
Flask
Jinja2
Install the required Python package:
pip install requirements.txt

Setup and Usage
1. Start the Flask API
Run the Flask API to handle configuration generation and deployment:
python main.py
The API will run on http://127.0.0.1:5000 by default.
2. Generate Terraform Configuration
Send a POST request to generate Terraform and Ansible configurations using the /generate-config endpoint.
Example Request
Use curl or an HTTP client like Postman to send the request:
curl -X POST http://127.0.0.1:5000/generate-config -H "Content-Type: application/json" -d '{
    "aws_region": "aws_region",
    "ami": "ami-id",
    "instance_type": "t2.micro",
    "num_replicas": 2,
    "key_name": "key_name",
    "postgresql_version": "13",
    "max_connections": "50",
    "shared_buffers": "128MB",
    "wal_level": "replica",
    "max_wal_senders": "replica"
}'
this will generate:

Terraform configuration (main.tf, variables.tf) to set up instances on AWS.
Ansible playbook (playbook.yml) to configure PostgreSQL settings.
3. Deploy Infrastructure
Once the configuration is generated, use the /apply endpoint to apply the Terraform plan and set up the EC2 instances:
curl -X POST http://127.0.0.1:5000/apply
Upon successful deployment, the API will create an Ansible inventory file with the IP addresses of the primary and replica instances.

4. Configure PostgreSQL
Run the Ansible playbook to set up PostgreSQL replication:
curl -X POST http://127.0.0.1:5000/configure
This step installs and configures PostgreSQL, setting up the primary-replica replication according to the provided variables.
