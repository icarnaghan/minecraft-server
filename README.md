# Minecraft Server on AWS

A simple Minecraft server deployment on AWS using CDK with Python, featuring easy management commands and automated setup.

## Features

- **Simple Deployment**: Single command deployment with `cdk deploy`
- **Cost Efficient**: Uses t4g.small ARM64 instance with minimal VPC setup
- **Secure**: Basic security group configuration for Minecraft and SSH access
- **Automated**: Complete server installation and configuration via user data
- **Managed**: Systemd service with auto-restart and boot startup
- **Easy Management**: Built-in commands for server administration

## Prerequisites

- AWS CLI configured with appropriate credentials
- Node.js and npm (for CDK CLI)
- Python 3.7+ with pip

## Quick Start

1. **Create SSH Key Pair**:
   ```bash
   aws ec2 create-key-pair --key-name minecraft --query 'KeyMaterial' --output text > minecraft.pem
   chmod 400 minecraft.pem
   ```

2. **Install CDK CLI**:
   ```bash
   npm install -g aws-cdk
   ```

3. **Bootstrap CDK** (first time only):
   ```bash
   cdk bootstrap
   ```

4. **Deploy the server**:
   ```bash
   # Activate virtual environment
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Deploy
   cdk deploy
   ```

5. **Get server IP**:
   After deployment, the public IP will be displayed in the output as `MinecraftServerIP`.

6. **Connect to Minecraft**:
   Use the public IP address in your Minecraft client to connect.

## Server Management

### Easy Management Commands

After deployment, SSH to your server and use these simple commands:

```bash
# SSH to your server
ssh -i minecraft.pem ec2-user@<PUBLIC_IP>

# Add players as operators
mc-op YourUsername
mc-op FriendUsername

# Check server status and recent activity
mc-status

# Follow live server logs (see players joining/leaving, chat, etc.)
mc-logs

# Restart server (useful after config changes)
mc-restart
```

### Available Management Commands

| Command | Description |
|---------|-------------|
| `mc-op <username>` | Add player as operator (automatically restarts server) |
| `mc-status` | Show server status and recent logs |
| `mc-restart` | Restart the server |
| `mc-logs` | Follow live server logs (Ctrl+C to exit) |

### Manual Server Management

If you prefer manual management:

```bash
# Control the systemd service
sudo systemctl start minecraft
sudo systemctl stop minecraft
sudo systemctl restart minecraft
sudo systemctl status minecraft

# View logs
sudo journalctl -u minecraft -f

# Edit server files
cd /opt/minecraft
sudo nano server.properties
sudo nano ops.json
sudo nano whitelist.json
```

## Server Configuration

- **Instance Type**: t4g.small (ARM64, 2 vCPU, 2GB RAM)
- **Java Version**: Amazon Corretto 21
- **Minecraft Version**: Latest server JAR
- **Memory Allocation**: 1GB (optimized for t4g.small)
- **Port**: 25565 (standard Minecraft port)
- **Max Players**: 20
- **Difficulty**: Easy
- **Game Mode**: Survival

### Customizing Server Settings

Edit server.properties for common settings:

```bash
# SSH to server and edit configuration
ssh -i minecraft.pem ec2-user@<PUBLIC_IP>
cd /opt/minecraft
sudo nano server.properties

# Common settings to modify:
# difficulty=easy                    # peaceful, easy, normal, hard
# gamemode=survival                 # survival, creative, adventure, spectator
# max-players=20                    # Maximum players
# pvp=true                          # Player vs Player combat
# white-list=false                  # Enable whitelist
# motd=Your Server Name             # Server description

# Restart server after changes
mc-restart
```

## In-Game Management

Once you're an operator, you can manage the server from within Minecraft:

```
/op <username>              # Make player an operator
/deop <username>            # Remove operator status
/whitelist add <username>   # Add to whitelist
/whitelist remove <username> # Remove from whitelist
/ban <username>             # Ban player
/pardon <username>          # Unban player
/gamemode creative <username> # Change player's game mode
/tp <player1> <player2>     # Teleport players
/time set day               # Set time to day
/weather clear              # Clear weather
```

## Troubleshooting

### Server Won't Start
```bash
# Check service status
mc-status

# View detailed logs
mc-logs

# Check Java version
java -version

# Restart server
mc-restart
```

### Can't Connect to Server
1. Check security group allows port 25565
2. Verify server is running: `mc-status`
3. Check public IP hasn't changed
4. Ensure Minecraft client version matches server

### Performance Issues
- Monitor with `mc-logs` for lag warnings
- Consider upgrading to larger instance type
- Reduce view-distance in server.properties
- Limit max-players if needed

## Cost Estimation

- t4g.small instance: ~$13/month
- VPC and networking: Free tier eligible
- Data transfer: Varies by usage
- Elastic IP (optional): $3.65/month when instance is stopped

## Security Notes

- SSH (port 22) and Minecraft (port 25565) are open to 0.0.0.0/0
- Consider restricting SSH access to your IP for production use
- Server runs as non-root user for security
- Regular backups recommended for world data

## Cleanup

To remove all resources:
```bash
cdk destroy
```

## Advanced Configuration

### Adding Mods/Plugins
1. SSH to server: `ssh -i minecraft.pem ec2-user@<PUBLIC_IP>`
2. Stop server: `mc-restart` 
3. Upload mod files to `/opt/minecraft/mods/` (create directory if needed)
4. Restart server: `mc-restart`

### Backup World Data
```bash
# Create backup
sudo tar -czf minecraft-backup-$(date +%Y%m%d).tar.gz -C /opt/minecraft world

# Download backup (from local machine)
scp -i minecraft.pem ec2-user@<PUBLIC_IP>:minecraft-backup-*.tar.gz ./
```

### Custom Server JAR
To use a different server version or modded server:
1. SSH to server
2. Stop server: `sudo systemctl stop minecraft`
3. Replace `/opt/minecraft/server.jar` with your custom JAR
4. Start server: `sudo systemctl start minecraft`