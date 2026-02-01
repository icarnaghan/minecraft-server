import pytest
import aws_cdk as cdk
from minecraft_server.minecraft_server_stack import MinecraftServerStack


def test_stack_creation():
    """Test that the stack can be created without errors."""
    app = cdk.App()
    stack = MinecraftServerStack(app, "TestStack")
    
    # Basic test - stack should be created successfully
    assert stack is not None
    assert stack.stack_name == "TestStack"


def test_stack_synthesis():
    """Test that the stack can be synthesized to CloudFormation."""
    app = cdk.App()
    stack = MinecraftServerStack(app, "TestStack")
    
    # Should be able to synthesize without errors
    template = app.synth().get_stack_by_name("TestStack").template
    assert template is not None


def test_security_group_rules():
    """Test that security group has correct ingress rules."""
    app = cdk.App()
    stack = MinecraftServerStack(app, "TestStack")
    template = app.synth().get_stack_by_name("TestStack").template
    
    # Find the security group resource
    security_groups = [
        resource for resource in template["Resources"].values()
        if resource["Type"] == "AWS::EC2::SecurityGroup"
        and "Minecraft" in resource.get("Properties", {}).get("GroupDescription", "")
    ]
    
    assert len(security_groups) == 1
    sg = security_groups[0]
    
    # Check ingress rules
    ingress_rules = sg["Properties"]["SecurityGroupIngress"]
    assert len(ingress_rules) == 2
    
    # Check for Minecraft port (25565)
    minecraft_rule = next(
        (rule for rule in ingress_rules if rule["FromPort"] == 25565), None
    )
    assert minecraft_rule is not None
    assert minecraft_rule["IpProtocol"] == "tcp"
    assert minecraft_rule["CidrIp"] == "0.0.0.0/0"
    
    # Check for SSH port (22)
    ssh_rule = next(
        (rule for rule in ingress_rules if rule["FromPort"] == 22), None
    )
    assert ssh_rule is not None
    assert ssh_rule["IpProtocol"] == "tcp"
    assert ssh_rule["CidrIp"] == "0.0.0.0/0"


def test_ec2_instance_configuration():
    """Test that EC2 instance has correct configuration."""
    app = cdk.App()
    stack = MinecraftServerStack(app, "TestStack")
    template = app.synth().get_stack_by_name("TestStack").template
    
    # Find the EC2 instance resource
    instances = [
        resource for resource in template["Resources"].values()
        if resource["Type"] == "AWS::EC2::Instance"
    ]
    
    assert len(instances) == 1
    instance = instances[0]
    
    # Check instance type
    assert instance["Properties"]["InstanceType"] == "t4g.small"
    
    # Check that it has security group attached
    assert "SecurityGroupIds" in instance["Properties"]
    assert len(instance["Properties"]["SecurityGroupIds"]) == 1
    
    # Check that it's in a public subnet
    assert "SubnetId" in instance["Properties"]


def test_user_data_script():
    """Test that user data script is properly configured."""
    app = cdk.App()
    stack = MinecraftServerStack(app, "TestStack")
    template = app.synth().get_stack_by_name("TestStack").template
    
    # Find the EC2 instance resource
    instances = [
        resource for resource in template["Resources"].values()
        if resource["Type"] == "AWS::EC2::Instance"
    ]
    
    assert len(instances) == 1
    instance = instances[0]
    
    # Check that user data is present
    assert "UserData" in instance["Properties"]
    
    # Decode the base64 user data to check contents
    import base64
    user_data_b64 = instance["Properties"]["UserData"]["Fn::Base64"]
    user_data = user_data_b64  # Already decoded in template
    
    # Check for key installation steps
    assert "java-17-amazon-corretto-headless" in user_data
    assert "useradd -r -m -U -d /opt/minecraft" in user_data
    assert "server.jar" in user_data
    assert "eula=true" in user_data
    assert "server.properties" in user_data
    
    # Check for systemd service configuration
    assert "minecraft.service" in user_data
    assert "User=minecraft" in user_data
    assert "Restart=always" in user_data
    assert "systemctl enable minecraft.service" in user_data
    assert "systemctl start minecraft.service" in user_data


def test_stack_outputs():
    """Test that stack outputs are properly configured."""
    app = cdk.App()
    stack = MinecraftServerStack(app, "TestStack")
    template = app.synth().get_stack_by_name("TestStack").template
    
    # Check that outputs section exists
    assert "Outputs" in template
    
    # Check for MinecraftServerIP output
    outputs = template["Outputs"]
    assert "MinecraftServerIP" in outputs
    
    server_ip_output = outputs["MinecraftServerIP"]
    assert "Description" in server_ip_output
    assert "Public IP address of the Minecraft server" in server_ip_output["Description"]
    assert "Value" in server_ip_output