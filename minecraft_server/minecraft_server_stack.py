from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
)
from constructs import Construct

class MinecraftServerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a simple VPC with public subnets only (minimal configuration)
        vpc = ec2.Vpc(
            self, "MinecraftVPC",
            max_azs=2,
            nat_gateways=0,  # No NAT gateways for simplicity and cost
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ]
        )

        # Create security group for Minecraft server
        security_group = ec2.SecurityGroup(
            self, "MinecraftSecurityGroup",
            vpc=vpc,
            description="Security group for Minecraft server",
            allow_all_outbound=True
        )

        # Allow Minecraft client connections (port 25565)
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(25565),
            description="Minecraft server port"
        )

        # Allow SSH access (port 22)
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="SSH access"
        )

        # Create EC2 instance
        instance = ec2.Instance(
            self, "MinecraftServer",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T4G, 
                ec2.InstanceSize.SMALL
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(
                cpu_type=ec2.AmazonLinuxCpuType.ARM_64
            ),
            vpc=vpc,
            security_group=security_group,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            user_data=ec2.UserData.for_linux(),
            # Add key pair for SSH access
            key_name="minecraft"
        )

        # Add user data script for Minecraft installation
        instance.user_data.add_commands(
            "#!/bin/bash",
            "set -e",
            "",
            "# Update system packages",
            "dnf update -y",
            "",
            "# Install Java 21 (Amazon Corretto)",
            "dnf install -y java-21-amazon-corretto-headless",
            "",
            "# Verify Java installation",
            "java -version",
            "",
            "# Create minecraft user and directory",
            "useradd -r -m -U -d /opt/minecraft -s /bin/bash minecraft",
            "mkdir -p /opt/minecraft",
            "chown minecraft:minecraft /opt/minecraft",
            "",
            "# Download Minecraft server JAR",
            "cd /opt/minecraft",
            "wget -O server.jar https://piston-data.mojang.com/v1/objects/4707d00eb834b446575d89a61a11b5d548d8c001/server.jar",
            "chown minecraft:minecraft server.jar",
            "",
            "# Accept EULA",
            "echo 'eula=true' > eula.txt",
            "chown minecraft:minecraft eula.txt",
            "",
            "# Create basic server.properties",
            "cat > server.properties << 'EOF'",
            "server-port=25565",
            "online-mode=true",
            "difficulty=easy",
            "gamemode=survival",
            "max-players=20",
            "motd=Simple Minecraft Server",
            "EOF",
            "chown minecraft:minecraft server.properties",
            "",
            "# Create systemd service file",
            "cat > /etc/systemd/system/minecraft.service << 'EOF'",
            "[Unit]",
            "Description=Minecraft Server",
            "After=network.target",
            "",
            "[Service]",
            "Type=simple",
            "User=minecraft",
            "Group=minecraft",
            "WorkingDirectory=/opt/minecraft",
            "ExecStart=/usr/bin/java -Xmx1024M -Xms1024M -jar server.jar nogui",
            "Restart=always",
            "RestartSec=10",
            "",
            "[Install]",
            "WantedBy=multi-user.target",
            "EOF",
            "",
            "# Enable and start Minecraft service",
            "systemctl daemon-reload",
            "systemctl enable minecraft.service",
            "systemctl start minecraft.service",
            "",
            "# Create easy management scripts",
            "echo 'Creating management scripts...'",
            "",
            "# Script to add operators easily",
            "cat > /usr/local/bin/mc-op << 'EOF'",
            "#!/bin/bash",
            "if [ -z \"$1\" ]; then",
            "    echo \"Usage: mc-op <username>\"",
            "    exit 1",
            "fi",
            "cd /opt/minecraft",
            "echo '[{\"name\":\"'$1'\",\"level\":4,\"bypassesPlayerLimit\":false}]' > ops.json",
            "chown minecraft:minecraft ops.json",
            "systemctl restart minecraft",
            "echo \"Added $1 as operator and restarted server\"",
            "EOF",
            "chmod +x /usr/local/bin/mc-op",
            "",
            "# Script to view server status and logs",
            "cat > /usr/local/bin/mc-status << 'EOF'",
            "#!/bin/bash",
            "echo \"=== Minecraft Server Status ===\"",
            "systemctl status minecraft --no-pager -l",
            "echo \"\"",
            "echo \"=== Recent Logs ===\"",
            "journalctl -u minecraft --no-pager -n 10",
            "EOF",
            "chmod +x /usr/local/bin/mc-status",
            "",
            "# Script to restart server",
            "cat > /usr/local/bin/mc-restart << 'EOF'",
            "#!/bin/bash",
            "echo \"Restarting Minecraft server...\"",
            "systemctl restart minecraft",
            "sleep 5",
            "systemctl status minecraft --no-pager",
            "EOF",
            "chmod +x /usr/local/bin/mc-restart",
            "",
            "# Script to follow live logs",
            "cat > /usr/local/bin/mc-logs << 'EOF'",
            "#!/bin/bash",
            "echo \"Following Minecraft server logs (Ctrl+C to exit)...\"",
            "journalctl -u minecraft -f",
            "EOF",
            "chmod +x /usr/local/bin/mc-logs",
            "",
            "echo \"\"",
            "echo \"=== Minecraft Server Management Commands ===\"",
            "echo \"mc-op <username>  - Add player as operator\"",
            "echo \"mc-status         - Show server status and recent logs\"",
            "echo \"mc-restart        - Restart the server\"",
            "echo \"mc-logs           - Follow live server logs\"",
            "echo \"\"",
            "echo \"Server setup complete! Use 'mc-op <username>' to add operators.\"",
        )

        # Output the public IP address
        CfnOutput(
            self, "MinecraftServerIP",
            value=instance.instance_public_ip,
            description="Public IP address of the Minecraft server"
        )
