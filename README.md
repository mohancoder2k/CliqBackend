# 🛡️ Project Risk Monitor Bot

##  Introduction
This bot was built to help project teams stay informed and proactive about risks — without needing to dig through dashboards or reports. Whether you're a project owner or a contributor, you can trigger key actions like `CHECK` or `ALERT` directly from Zoho Cliq. It’s lightweight, secure, and designed for real-world usage.

---


## Architecture

![CliqToProject Architecture](https://github.com/mohancoder2k/CliqBackend/blob/main/images/arch.png?raw=true)

This diagram illustrates the end-to-end flow of the CliqToProject bot:

- **Zoho Cliq (User Interaction Layer)**  
  A user sends a message like `CHECK` or `ALERT` to the bot. The bot uses a Participation Handler to normalize and validate the input. It then routes the message to the backend via an incoming webhook, attaching a secure header (`X-Webhook-Token`) for authentication.

- **Backend (Flask on Render)**  
  The Flask server receives the webhook payload and decides the action:
  - If the message is `CHECK`, it triggers a POST to `/webhook/cliq`
  - If the message is `ALERT`, it triggers a POST to `/digest`  
  All requests are logged and validated defensively.

- **Zoho Projects (Data Layer)**  
  The backend interacts with Zoho Projects using its REST API. It fetches task status or sends alerts/digests. OAuth tokens are exchanged and refreshed securely, with scoped access to ensure minimal permissions.

- **Response Flow**  
  Once the backend receives a response from Zoho Projects, it formats the result and pushes it back to the Zoho Cliq bot, which replies to the user with a confirmation or status update.

This architecture ensures secure, reliable, and real-time communication between Zoho Cliq and Zoho Projects, powered by a lightweight Flask backend hosted on Render.

## 📄 Documented PDF

[📥 Click here to view the full documentation (PDF)](https://drive.google.com/file/d/1rUWQzleS3DKUcb5u34LLMSIl5hxTJSAF/view?usp=sharing)

## 🚀 Features
- **CHECK** → Sends a secure POST request to `/webhook/cliq` to fetch or log current project status.
- **ALERT** → Sends a secure POST to `/digest` to trigger a risk digest or escalation.
- **Simple UI** → Users can type `CHECK` or `ALERT` directly in chat. No menus required.
- **Secure by Design** → All backend calls are protected with token-based headers (`X-Webhook-Token`).

---

## 💬 Usage
Type one of the following in the bot chat:
- `CHECK` → to fetch current status
- `ALERT` → to trigger a digest or escalation

If you type anything else (like `.` or `hi`), the bot gently reminds you:
> “Send CHECK or ALERT.”

---

## 🔐 Security
- All POST requests include a custom header:  
  `X-Webhook-Token: 5566aabbcc`
- No sensitive data is exposed in the bot UI.
- Backend endpoints are hosted securely on Render.

---

## 🧱 Tech Stack
- **Zoho Cliq Bot** (Deluge scripting)
- **Flask Backend** (Python)
- **Render Hosting**
- **Token-based Auth**
- **Interactive UI (optional)** via button cards

---

## 🧪 Testing
1. Type `CHECK` or `ALERT` in the bot chat
2. Confirm backend logs show POST requests
3. Try sending `.` or `hello` to see fallback message
4. Backend should respond with `200 OK` and log the request

---

## 📦 Deployment Notes
- Backend endpoints are live at:
  - `https://cliqbackend.onrender.com/webhook/cliq`
  - `https://cliqbackend.onrender.com/digest`
- Bot is configured with a Participation Handler for chat input
- Menu Handler is optional and can be used to show buttons

---

## 🏁 Final Notes
This bot is built for reliability and clarity. It doesn’t rely on fancy UI — just solid backend routing and secure triggers. I hope it reflects thoughtful design, defensive coding, and real-world usability.
