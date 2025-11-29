# CliqToProject – Zoho Cliqtrix Contest Submission

## Overview
CliqToProject is a Zoho Cliq bot integrated with Zoho Projects to provide real-time project monitoring, task status checks, and automated alerts. 
The bot helps teams stay updated on project activities without manually checking dashboards. 
This system was developed end-to-end by overcoming challenges across Zoho Projects API integration, Zoho Cliq bot event handling, and Zoho Catalyst AppSail deployment.

## Key Features
- Command-based bot interaction inside Zoho Cliq.
- CHECK command triggers real-time task monitoring.
- ALERT command sends scheduled or immediate digest alerts.
- Backend built using Python (Flask) and hosted on Zoho Catalyst AppSail.
- Secure communication using Zoho OAuth and scoped API access.
- Logs and validations implemented for debugging and consistency.

## Architecture
1. User sends a message to the Zoho Cliq bot.
2. Zoho Cliq triggers an incoming webhook.
3. Flask backend (hosted on Catalyst AppSail) receives the payload.
4. Backend decides the action based on message text:
   - If message == "CHECK": POST request to `/webhook/cliq`
   - If message == "ALERT": POST request to `/digest`
5. Backend interacts with Zoho Projects API when needed.
6. Result is pushed back to Zoho Cliq via bot reply.

## Technology Stack
- Python (Flask)
- Zoho Catalyst AppSail
- Zoho Cliq Bot API
- Zoho Projects REST API
- HTTPS Webhooks

## Challenges Overcome
- Handling Zoho OAuth token refresh and authentication issues.
- Fixing invalid bot configurations and event routing.
- Debugging 400/401 errors from Zoho Projects API.
- Deploying Flask server successfully in Catalyst AppSail.
- Managing webhook structures and response formatting.
- Ensuring correct JSON structures for Zoho Cliq bot cards and messages.

## Endpoints
### POST /webhook/cliq
Receives Zoho Cliq messages and processes bot commands.

### POST /digest
Sends alert or digest notifications back to Cliq.

## Folder Structure
