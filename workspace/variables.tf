variable "aws_region" {
  default = "ap-south-1"
}

variable "ami" {
  default = "ami-08bf489a05e916bbd"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "num_replicas" {
  default = 2
}