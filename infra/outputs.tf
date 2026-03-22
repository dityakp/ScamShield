output "server_public_ip" {
  value       = aws_instance.scamshield_server.public_ip
  description = "Connect to this IP address when deployment is finished"
}
