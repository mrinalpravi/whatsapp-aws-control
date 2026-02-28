# Step 3: Lambda and API Gateway Setup

## 3.1 Create Lambda Function

### Option A: AWS Console

1. Go to **Lambda** > **Create function**
2. Choose **Author from scratch**
3. Configuration:
   - **Function name**: `whatsapp-ec2-control`
   - **Runtime**: `Python 3.11`
   - **Architecture**: `x86_64`
   - **Execution role**: Use existing role `WhatsAppEC2ControlLambdaRole`
4. Click **Create function**
5. In the **Code** tab:
   - Copy the contents of `lambda/handler.py`
   - Click **Deploy**
6. In **Configuration** > **General configuration**:
   - Set **Timeout** to `30 seconds`
7. In **Configuration** > **Environment variables**, add:
   - `WEBHOOK_URL`: (will be set after API Gateway creation)

### Option B: AWS CLI

```bash
# Create deployment package
cd lambda
zip function.zip handler.py

# Create Lambda function
aws lambda create-function \
  --function-name whatsapp-ec2-control \
  --runtime python3.11 \
  --handler handler.lambda_handler \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/WhatsAppEC2ControlLambdaRole \
  --zip-file fileb://function.zip \
  --timeout 30
```

## 3.2 Create API Gateway

### Option A: AWS Console

1. Go to **API Gateway** > **Create API**
2. Choose **HTTP API** > **Build**
3. Configuration:
   - **API name**: `whatsapp-ec2-webhook`
   - Click **Add integration** > **Lambda**
   - Select your `whatsapp-ec2-control` function
4. Configure routes:
   - **Method**: `POST`
   - **Resource path**: `/webhook`
5. Configure stages:
   - **Stage name**: `prod`
6. Click **Create**
7. Copy the **Invoke URL** (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com`)

### Option B: AWS CLI

```bash
# Create HTTP API
aws apigatewayv2 create-api \
  --name whatsapp-ec2-webhook \
  --protocol-type HTTP \
  --target arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:whatsapp-ec2-control

# Get the API ID
API_ID=$(aws apigatewayv2 get-apis --query "Items[?Name=='whatsapp-ec2-webhook'].ApiId" --output text)

# Create route
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "POST /webhook"

# Create stage
aws apigatewayv2 create-stage \
  --api-id $API_ID \
  --stage-name prod \
  --auto-deploy

# Get the endpoint URL
aws apigatewayv2 get-api --api-id $API_ID --query "ApiEndpoint"
```

## 3.3 Add Lambda Permission for API Gateway

```bash
aws lambda add-permission \
  --function-name whatsapp-ec2-control \
  --statement-id apigateway-access \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:YOUR_ACCOUNT_ID:$API_ID/*"
```

## 3.4 Update Lambda Environment Variable

After getting your API Gateway URL, update the Lambda:

```bash
aws lambda update-function-configuration \
  --function-name whatsapp-ec2-control \
  --environment "Variables={WEBHOOK_URL=https://abc123.execute-api.us-east-1.amazonaws.com/webhook}"
```

## 3.5 Your Webhook URL

Your final webhook URL will be:
```
https://{api-id}.execute-api.{region}.amazonaws.com/webhook
```

This is what you'll configure in Twilio (Step 1.4).
