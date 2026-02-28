# Step 2: IAM Role and Policy Setup

## 2.1 Create IAM Policy (Least Privilege)

Create a new IAM policy with **only** the required permissions.

### Option A: AWS Console

1. Go to **IAM** > **Policies** > **Create policy**
2. Choose **JSON** tab
3. Paste the policy from `iam/ec2-control-policy.json`
4. Name it: `WhatsAppEC2ControlPolicy`

### Option B: AWS CLI

```bash
aws iam create-policy \
  --policy-name WhatsAppEC2ControlPolicy \
  --policy-document file://iam/ec2-control-policy.json
```

## 2.2 Create IAM Role for Lambda

### AWS Console

1. Go to **IAM** > **Roles** > **Create role**
2. Select **AWS Service** > **Lambda**
3. Attach these policies:
   - `WhatsAppEC2ControlPolicy` (custom policy we created)
   - `AWSLambdaBasicExecutionRole` (for CloudWatch logs)
   - `SecretsManagerReadWrite` (or custom read-only for specific secret)
4. Name it: `WhatsAppEC2ControlLambdaRole`

### AWS CLI

```bash
# Create the role
aws iam create-role \
  --role-name WhatsAppEC2ControlLambdaRole \
  --assume-role-policy-document file://iam/lambda-trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name WhatsAppEC2ControlLambdaRole \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/WhatsAppEC2ControlPolicy

aws iam attach-role-policy \
  --role-name WhatsAppEC2ControlLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

## 2.3 Store Secrets in AWS Secrets Manager

```bash
aws secretsmanager create-secret \
  --name whatsapp-ec2-control/twilio \
  --secret-string '{
    "TWILIO_ACCOUNT_SID": "ACxxxxxxxxxxxxxxxxxxxxxxxxx",
    "TWILIO_AUTH_TOKEN": "your-auth-token",
    "ALLOWED_PHONE_NUMBERS": "+1234567890"
  }'
```

## Security Best Practices Applied

- **No wildcard resources** - Only tagged instances can be controlled
- **Condition-based access** - EC2 actions restricted by tag
- **Read-only describe** - Can describe all instances but only act on tagged ones
- **Secrets in Secrets Manager** - No hardcoded credentials
- **CloudWatch logging** - All actions are logged
