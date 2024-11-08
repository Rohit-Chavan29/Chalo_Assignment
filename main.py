from flask import Flask, request, jsonify
from jinja2 import Environment, FileSystemLoader
import subprocess
import os
import json

app = Flask(__name__)

# Paths
workspace_path = "workspace"
template_path = "templates"

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader(template_path))

# Generate Terraform and Ansible configurations
def generate_config(params):
    try:
        params.setdefault("max_connections", 50)
        params.setdefault("shared_buffers", "128MB")
        if "max_connections" not in params or "shared_buffers" not in params:
            raise ValueError("Required parameters max_connections or shared_buffers missing")
        print("Params received:", params)
        # Render Terraform main.tf
        
        tf_template = env.get_template("main.tf.j2")
       
        tf_content = tf_template.render(params=params)  
        with open(os.path.join(workspace_path, "main.tf"), "w") as f:
            f.write(tf_content)
            
        # Render Terraform variables.tf
        variables_template = env.get_template("variables.tf.j2")
        variables_content = variables_template.render(params=params)  
        with open(os.path.join(workspace_path, "variables.tf"), "w") as f:
            f.write(variables_content)

        # Render Ansible playbook.yml
        
        ansible_template = env.get_template("playbook.yml.j2")
        
        
        
        ansible_content = ansible_template.render(params=params)
       
        with open(os.path.join(workspace_path, "playbook.yml"), "w") as f:
            f.write(ansible_content)

        return {"message": "Configuration generated successfully."}, 200

    except Exception as e:
        return {"error": str(e)}, 500

# Endpoint to generate configuration
@app.route('/generate-config', methods=['POST'])
def generate_config_endpoint():
    params = request.json
    response, status_code = generate_config(params)
    return jsonify(response), status_code
# Apply infrastructure with Terraform
@app.route('/apply', methods=['POST'])
def apply_infrastructure():
    try:
        # Initialize and apply Terraform
        subprocess.run(["terraform", "init"], cwd=workspace_path, check=True)
        subprocess.run(["terraform", "plan"], cwd=workspace_path, check=True)
        subprocess.run(["terraform", "apply", "-auto-approve"], cwd=workspace_path, check=True)

        # Capture instance IPs from Terraform output
        primary_ip = subprocess.check_output(
            ["terraform", "output", "-raw", "primary_instance_ip"], cwd=workspace_path
        ).strip().decode("utf-8")
        
        replica_ips = json.loads(subprocess.check_output(
            ["terraform", "output", "-json", "replica_instance_ips"], cwd=workspace_path
        ))

        # Generate Ansible inventory file
        with open(os.path.join(workspace_path, "inventory"), "w") as f:
            f.write("[primary]\n")
            f.write(f"{primary_ip} ansible_user=ec2-user ansible_ssh_private_key_file=/home/rohit/Downloads/amazon_login.pem\n\n")
            f.write("[replicas]\n")
            for ip in replica_ips:
                f.write(f"{ip} ansible_user=ec2-user ansible_ssh_private_key_file=/home/rohit/Downloads/amazon_login.pem\n")

        return jsonify({"message": "Infrastructure applied and inventory file generated successfully."}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Terraform apply failed", "details": str(e)}), 500

# Configure PostgreSQL using Ansible
@app.route('/configure', methods=['POST'])
def configure_postgresql():
    try:
        # Run Ansible playbook using the generated inventory file
        subprocess.run(
            ["ansible-playbook", "-i", os.path.join(workspace_path, "inventory"), os.path.join(workspace_path, "playbook.yml")],
            check=True
        )
        return jsonify({"message": "PostgreSQL configured successfully."}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Ansible playbook failed", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
