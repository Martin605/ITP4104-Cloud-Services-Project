from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_cloudformation as cloudformation,
    core
    )
    
class VpcStack(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Exercise 3
        # Create VPC
        vpc = ec2.CfnVPC(self, "VPC",
            cidr_block = "10.1.0.0/16",
            tags = [{
                "key" : "Name",
                "value" : "edx-build-aws-vpc"
            }]
        )
        
        # Create Internet Gateway
        internet_gateway = ec2.CfnInternetGateway(self, "InternetGateway",
            tags = [{
                "key" : "Name",
                "value" : "edx-igw"
            }]
        )
        
        # Attach Gateway
        attach_gateway = ec2.CfnVPCGatewayAttachment(self, "AttachGateway",
            vpc_id = vpc.ref,
            internet_gateway_id = internet_gateway.ref
        )
        
        # Create EIP1
        eip_1 = ec2.CfnEIP(self, "EIP1",
            domain = "vpc"
        )
        
        # Create Public Subnet 1
        public_subnet_1 = ec2.CfnSubnet(self, "PublicSubnet1",
            availability_zone = "us-east-1a",
            cidr_block = "10.1.1.0/24",
            vpc_id = vpc.ref,
            map_public_ip_on_launch = True,
            tags = [{
                "key" : "Name",
                "value" : "edx-subnet-public-a"
            }]
        )

        # Create Nat Gateway 1
        nat_gateway_1 = ec2.CfnNatGateway(self, "NatGateway1",
            allocation_id = eip_1.attr_allocation_id, 
            subnet_id = public_subnet_1.ref
        )
        
        # Create Private Route Table 1
        private_route_table_1 = ec2.CfnRouteTable(self, "PrivateRouteTable1",
            vpc_id = vpc.ref,
            tags = [{
                "key" : "Name",
                "value" : "edx-routetable-private1"
            }]
        )
        
        # Create Private Route 1
        private_route_1 = ec2.CfnRoute(self, "PrivateRoute1",
            route_table_id = private_route_table_1.ref,
            destination_cidr_block = "0.0.0.0/0",
            nat_gateway_id = nat_gateway_1.ref
        )
        
        # Create EIP2
        eip_2 = ec2.CfnEIP(self, "EIP2",
            domain = "vpc"
        )
        
        # Create Public Subnet 2
        public_subnet_2 = ec2.CfnSubnet(self, "PublicSubnet2",
            availability_zone = "us-east-1b",
            cidr_block = "10.1.2.0/24",
            vpc_id = vpc.ref,
            map_public_ip_on_launch = True,
            tags = [{
                "key" : "Name",
                "value" : "edx-subnet-public-b"
            }]
        )
        
        # Create Nat Gateway 2
        nat_gateway_2 = ec2.CfnNatGateway(self, "NatGateway2",
            allocation_id = eip_2.attr_allocation_id, 
            subnet_id = public_subnet_2.ref
        )
        
        # Create Private Route Table 2
        private_route_table_2 = ec2.CfnRouteTable(self, "PrivateRouteTable2",
            vpc_id = vpc.ref,
            tags = [{
                "key" : "Name",
                "value" : "edx-routetable-private2"
            }]
        )
        
        # Create Private Route 2
        private_route_2 = ec2.CfnRoute(self, "PrivateRoute2",
            route_table_id = private_route_table_2.ref,
            destination_cidr_block = "0.0.0.0/0",
            nat_gateway_id = nat_gateway_2.ref
        )
        
        # Create Public Route Table
        public_route_table = ec2.CfnRouteTable(self, "PublicRouteTable",
        vpc_id = vpc.ref,
        tags = [{
                "key" : "Name",
                "value" : "edx-routetable-public"
        }]
        )
        
        # Create Public Default Route
        public_default_route = ec2.CfnRoute(self, "PublicDefaultRoute",
            route_table_id = public_route_table.ref,
            destination_cidr_block = "0.0.0.0/0",
            gateway_id = internet_gateway.ref
        )
        
        # Create Public Route Association 1
        public_route_association_1 = ec2.CfnSubnetRouteTableAssociation(self, "PublicRouteAssociation1",
            route_table_id = public_route_table.ref,
            subnet_id = public_subnet_1.ref
        )
        
        # Create Public Route Association 12
        public_route_association_2 = ec2.CfnSubnetRouteTableAssociation(self, "PublicRouteAssociation2",
            route_table_id = public_route_table.ref,
            subnet_id = public_subnet_2.ref
        )
        
        # Create Private Subnet 1
        private_subnet_1 = ec2.CfnSubnet(self, "PrivateSubnet1",
            availability_zone = "us-east-1a",
            cidr_block = "10.1.3.0/24",
            vpc_id = vpc.ref,
            tags = [{
                "key" : "Name",
                "value" : "edx-subnet-private-a"
            }]
        )
        
        # Create Private Subnet 2
        private_subnet_2 = ec2.CfnSubnet(self, "PrivateSubnet2",
            availability_zone = "us-east-1b",
            cidr_block = "10.1.4.0/24",
            vpc_id = vpc.ref,
            tags = [{
                "key" : "Name",
                "value" : "edx-subnet-private-b"
            }]
        )
        
        # Create Private Route Association 1
        private_route_association_1 = ec2.CfnSubnetRouteTableAssociation(self, "PrivateRouteAssociation1",
            route_table_id = private_route_table_1.ref,
            subnet_id = private_subnet_1.ref
        )
        
        # Create Private Route Association 2
        private_route_association_1 = ec2.CfnSubnetRouteTableAssociation(self, "PrivateRouteAssociation2",
            route_table_id = private_route_table_2.ref,
            subnet_id = private_subnet_2.ref
        )
        
        # Output
        core.CfnOutput(self, "VPCOutput",
            value = vpc.ref,
            description = "VPC",
            export_name = "VPC"
        )
        core.CfnOutput(self, "PublicSubnet1Output",
            value = public_subnet_1.ref,
            description = "PublicSubnet1",
            export_name = "PublicSubnet1"
        )
        core.CfnOutput(self, "PublicSubnet2Output",
            value = public_subnet_2.ref,
            description = "PublicSubnet2",
            export_name = "PublicSubnet2"
        )
        core.CfnOutput(self, "PrivateSubnet1Output",
            value = private_subnet_1.ref,
            description = "PrivateSubnet1",
            export_name = "PrivateSubnet1"
        )
        core.CfnOutput(self, "PrivateSubnet2Output",
            value = private_subnet_2.ref,
            description = "PrivateSubnet2",
            export_name = "PrivateSubnet2"
        )