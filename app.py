#!/usr/bin/env python3
import os

import aws_cdk as cdk

from minecraft_server.minecraft_server_stack import MinecraftServerStack


app = cdk.App()
MinecraftServerStack(app, "MinecraftServerStack",
    # Use current CLI configuration for account/region
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
)

app.synth()
