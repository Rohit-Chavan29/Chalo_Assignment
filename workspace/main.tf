provider "aws" {
  region = "ap-south-1"
}
resource "aws_security_group" "postgres_sg" {
  name_prefix = "postgres-sg"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # replace with a more restrictive IP range if possible
  }
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_instance" "primary" {
  ami           = "ami-08bf489a05e916bbd"
  instance_type = "t2.micro"
  security_groups = [aws_security_group.postgres_sg.name]
  key_name      = "amazon_login" 
  tags = {
    Name = "PostgresPrimary"
  }
}

resource "aws_instance" "replica" {
  count         = 2
  ami           = "ami-08bf489a05e916bbd"
  instance_type = "t2.micro"
  security_groups = [aws_security_group.postgres_sg.name]
  key_name      = "amazon_login" 

  tags = {
    Name = "PostgresReplica-${count.index}"
  }
}
output "primary_instance_ip" {
  value = aws_instance.primary.public_ip
  description = "The public IP address of the primary instance"
}

output "replica_instance_ips" {
  value = aws_instance.replica[*].public_ip
  description = "The public IP addresses of the replica instances"
}