# WhatsApp EC2 Control Bot

Control your AWS EC2 instances via WhatsApp messages. Stop and start instances tagged with `Environment=Dev` or `AutoStop=True` using simple text commands.

## Quick Start

```bash
# Install SAM CLI
pip install aws-sam-cli

# Deploy
sam build && sam deploy --guided
```

Then configure the webhook URL in your Twilio WhatsApp Sandbox.

## Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `status` | List all controllable instances |
| `stop dev` | Stop Environment=Dev instances |
| `start dev` | Start Environment=Dev instances |
| `stop auto` | Stop AutoStop=True instances |
| `start auto` | Start AutoStop=True instances |

## Architecture

```
WhatsApp → Twilio → API Gateway → Lambda → EC2
```

## Setup Steps

1. **[Step 1: Twilio Setup](STEP1_TWILIO_SETUP.md)** - Create Twilio account and configure WhatsApp
2. **[Step 2: IAM Setup](STEP2_IAM_SETUP.md)** - Create least-privilege IAM role
3. **[Step 3: Lambda & API Gateway](STEP3_LAMBDA_APIGATEWAY.md)** - Deploy the webhook
4. **[Step 4: Deployment](STEP4_DEPLOYMENT.md)** - Deploy and test

## Project Structure

```
whatsapp-ec2-control/
├── README.md
├── ARCHITECTURE.md
├── template.yaml              # SAM/CloudFormation template
├── iam/
│   ├── ec2-control-policy.json
│   └── lambda-trust-policy.json
├── lambda/
│   ├── handler.py             # Lambda function code
│   └── requirements.txt
├── STEP1_TWILIO_SETUP.md
├── STEP2_IAM_SETUP.md
├── STEP3_LAMBDA_APIGATEWAY.md
└── STEP4_DEPLOYMENT.md
```

## Security Features

- **Twilio signature validation** - Verifies requests come from Twilio
- **Phone number allowlist** - Only authorized numbers can control instances
- **Least-privilege IAM** - Lambda can only control tagged instances
- **Secrets Manager** - No hardcoded credentials
- **HTTPS only** - All communication encrypted

## Tag Your EC2 Instances

For the bot to control your instances, add one of these tags:

```bash
# For Dev environment instances
aws ec2 create-tags \
  --resources i-1234567890abcdef0 \
  --tags Key=Environment,Value=Dev

# For auto-stop instances
aws ec2 create-tags \
  --resources i-1234567890abcdef0 \
  --tags Key=AutoStop,Value=True
```

## Cost

- **Lambda**: ~$0.20/million requests (free tier: 1M/month)
- **API Gateway**: ~$1.00/million requests (free tier: 1M/month for 12 months)
- **Secrets Manager**: ~$0.40/month per secret
- **Twilio**: WhatsApp Sandbox is free for testing

## License

MIT
