region         = "ap-southeast-1"
vpc_id         = "vpc-04dc5b9dc6bc72980"
subnet_id      = "subnet-08683049b23c017be"
instance_name  = "graviton-ssm-agent"
iam_role_arn   = "arn:aws:iam::973314620257:role/MANAGED"
instance_type = "t4g.small"
security_group_name     = "graviton-ec2-sg"
instance_profile_name  = "graviton-ssm-profile"

user_data = <<EOF
#!/bin/bash
yum install -y amazon-ssm-agent
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent
EOF
