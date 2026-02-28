# WhatsApp EC2 Control Bot - Architecture

## Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    WhatsApp     │────▶│     Twilio      │────▶│  API Gateway    │────▶│     Lambda      │
│    (User)       │◀────│   WhatsApp API  │◀────│   (Webhook)     │◀────│   (Handler)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                                                  │
                                                                                  ▼
                                                                         ┌─────────────────┐
                                                                         │      EC2        │
                                                                         │   (Tagged)      │
                                                                         └─────────────────┘
```

## Components

1. **Twilio WhatsApp API** - Receives WhatsApp messages and forwards to webhook
2. **API Gateway** - HTTPS endpoint that receives Twilio webhooks
3. **Lambda Function** - Processes commands and controls EC2 instances
4. **IAM Role** - Least-privilege permissions for Lambda
5. **EC2 Instances** - Tagged instances to be controlled

## Supported Commands

| Message | Action |
|---------|--------|
| `stop dev` | Stop all instances with `Environment=Dev` |
| `start dev` | Start all instances with `Environment=Dev` |
| `stop auto` | Stop all instances with `AutoStop=True` |
| `start auto` | Start all instances with `AutoStop=True` |
| `status` | List all tagged instances and their states |
| `help` | Show available commands |

## Security Features

- Twilio request signature validation
- Allowlist of phone numbers
- IAM least-privilege principle
- No hardcoded credentials (uses IAM roles)
- API Gateway with HTTPS only
