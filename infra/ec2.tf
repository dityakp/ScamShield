resource "aws_instance" "scamshield_server" {
  ami           = var.ami_id
  instance_type = var.instance_type
  
  vpc_security_group_ids = [aws_security_group.scamshield_sg.id]

  # Make it easily identifiable in AWS
  tags = {
    Name = "ScamShield-Production"
  }

  # Automate Docker Installation exactly when the server turns on
  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update -y
              sudo apt-get install -y docker.io docker-compose git
              sudo systemctl start docker
              sudo systemctl enable docker
              sudo usermod -aG docker ubuntu
              EOF
}
