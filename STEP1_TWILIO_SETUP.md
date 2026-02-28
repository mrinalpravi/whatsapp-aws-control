# Step 1: Twilio WhatsApp Setup

## 1.1 Create Twilio Account

1. Go to https://www.twilio.com and create an account
2. Verify your email and phone number
3. Navigate to **Console Dashboard**

## 1.2 Enable WhatsApp Sandbox (for Development)

1. Go to **Messaging** > **Try it out** > **Send a WhatsApp message**
2. Follow the instructions to join the sandbox:
   - Send "join <your-sandbox-keyword>" to the Twilio sandbox number
   - Example: Send "join flying-elephant" to +1 415 523 8886
3. Save your sandbox number for testing

## 1.3 Get Twilio Credentials

1. Go to **Console Dashboard**
2. Copy these values (you'll need them later):
   - **Account SID**: `ACxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **Auth Token**: `xxxxxxxxxxxxxxxxxxxxxxxxx`

## 1.4 Configure Webhook (After Lambda/API Gateway Setup)

Once you have your API Gateway URL:

1. Go to **Messaging** > **Try it out** > **Send a WhatsApp message**
2. In the **Sandbox Configuration** section:
   - **When a message comes in**: `https://your-api-gateway-url/webhook`
   - **HTTP Method**: `POST`
3. Click **Save**

## 1.5 For Production: WhatsApp Business API

For production use:

1. Go to **Messaging** > **Senders** > **WhatsApp senders**
2. Click **Add new sender**
3. Complete the WhatsApp Business verification process
4. This requires:
   - Facebook Business Manager account
   - Verified business
   - WhatsApp Business API approval

## 1.6 Store Credentials Securely

Store these in AWS Secrets Manager (we'll set this up later):

```json
{
  "TWILIO_ACCOUNT_SID": "ACxxxxxxxxxxxxxxxxxxxxxxxxx",
  "TWILIO_AUTH_TOKEN": "your-auth-token",
  "ALLOWED_PHONE_NUMBERS": "+1234567890,+0987654321"
}
```
