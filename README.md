
# Minecraft Server on AWS

A simple Minecraft server deployment on AWS using CDK with Python.

## Features

- **Simple Deployment**: Single command deployment with `cdk deploy`
- **Cost Efficient**: Uses t4g.small ARM64 instance with minimal VPC setup
- **Secure**: Basic security group configuration for Minecraft and SSH access
- **Automated**: Complete server installation and configuration via user data
- **Managed**: Systemd service with auto-restart and boot startup

## Prerequisites

- AWS CLI configured with appropriate credentials
- Node.js and npm (for CDK CLI)
- Python 3.7+ with pip

## Quick Start

1. **Install CDK CLI**:
   ```bash
   npm install -g aws-cdk
   ```

2. **Bootstrap CDK** (first time only):
   ```bash
   cdk bootstrap
   ```

3. **Deploy the server**:
   ```bash
   # Activate virtual environment
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Deploy
   cdk deploy
   ```

4. **Get server IP**:
   After deployment, the public IP will be displayed in the output as `MinecraftServerIP`.

5. **Connect to Minecraft**:
   Use the public IP address in your Minecraft client to connect.

## Server Configuration

- **Instance Type**: t4g.small (ARM64)
- **Java Version**: Amazon Corretto 17
- **Minecraft Version**: Latest server JAR
- **Memory**: 1GB allocated to Minecraft
- **Port**: 25565 (standard Minecraft port)
- **Max Players**: 20
- **Difficulty**: Easy
- **Game Mode**: Survival

## Management

- **SSH Access**: Use the public IP with your key pair
- **Service Control**: 
  ```bash
  sudo systemctl status minecraft
  sudo systemctl restart minecraft
  sudo systemctl stop minecraft
  ```
- **Logs**: `sudo journalctl -u minecraft -f`

## Cleanup

To remove all resources:
```bash
cdk destroy
```

## Cost Estimation

- t4g.small instance: ~$13/month
- VPC and networking: Free tier eligible
- Data transfer: Varies by usage

## Security Notes

- SSH (port 22) and Minecraft (port 25565) are open to 0.0.0.0/0
- Consider restricting SSH access to your IP for production use
- Server runs as non-root user for security
