# Step 4: Deployment

## Prerequisites

- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed (`pip install aws-sam-cli`)
- Twilio account with WhatsApp Sandbox configured

## Option A: Deploy with SAM (Recommended)

### 4.1 Build the Application

```bash
cd /path/to/whatsapp-ec2-control
sam build
```

### 4.2 Deploy

```bash
sam deploy --guided
```

You'll be prompted for:
- **Stack Name**: `whatsapp-ec2-control`
- **AWS Region**: Your preferred region (e.g., `us-east-1`)
- **TwilioAccountSid**: Your Twilio Account SID
- **TwilioAuthToken**: Your Twilio Auth Token
- **AllowedPhoneNumbers**: Your WhatsApp number (e.g., `+1234567890`)

### 4.3 Get the Webhook URL

After deployment, note the output:
```
Outputs
-----------------------------------------
WebhookUrl: https://abc123.execute-api.us-east-1.amazonaws.com/webhook
```

### 4.4 Configure Twilio

1. Go to Twilio Console > Messaging > WhatsApp Sandbox
2. Set the webhook URL to the `WebhookUrl` from outputs
3. Set HTTP method to `POST`
4. Save

## Option B: Manual Deployment

Follow these steps in order:

1. **Step 2**: Create IAM role and policy
2. **Step 3**: Create Lambda function and API Gateway
3. **Step 1.4**: Configure Twilio webhook

## Testing

### Test via WhatsApp

1. Send a message to your Twilio WhatsApp number
2. Try these commands:
   - `help` - See available commands
   - `status` - See all controllable instances
   - `stop dev` - Stop Dev environment instances

### Test Lambda Directly

```bash
# Create test event
cat > test-event.json << 'EOF'
{
  "body": "Qm9keT1oZWxwJkZyb209JTJCMTIzNDU2Nzg5MA==",
  "isBase64Encoded": true,
  "headers": {
    "Content-Type": "application/x-www-form-urlencoded"
  }
}
EOF

# Invoke Lambda
aws lambda invoke \
  --function-name whatsapp-ec2-control \
  --payload file://test-event.json \
  response.json

cat response.json
```

## Troubleshooting

### Check CloudWatch Logs

```bash
aws logs tail /aws/lambda/whatsapp-ec2-control --follow
```

### Common Issues

1. **403 Forbidden**
   - Check that your phone number is in the allowed list
   - Verify Twilio signature validation

2. **No instances found**
   - Ensure EC2 instances are tagged with `Environment=Dev` or `AutoStop=True`
   - Check IAM permissions

3. **Timeout**
   - Increase Lambda timeout (default: 30s)

## Cleanup

To remove all resources:

```bash
sam delete --stack-name whatsapp-ec2-control
```

Or manually:
```bash
aws lambda delete-function --function-name whatsapp-ec2-control
aws iam delete-role-policy --role-name WhatsAppEC2ControlLambdaRole --policy-name EC2ControlPolicy
aws iam delete-role --role-name WhatsAppEC2ControlLambdaRole
aws secretsmanager delete-secret --secret-id whatsapp-ec2-control/twilio --force-delete-without-recovery
```
