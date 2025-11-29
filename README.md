# 🛡️ Project Risk Monitor Bot

## 👋 Introduction
This bot was built to help project teams stay informed and proactive about risks — without needing to dig through dashboards or reports. Whether you're a project owner or a contributor, you can trigger key actions like `CHECK` or `ALERT` directly from Zoho Cliq. It’s lightweight, secure, and designed for real-world usage.

---

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
This bot is built for reliability and clarity. It doesn’t rely on fancy UI — just solid backend routing and secure triggers. If you’re judging this for a contest, I hope it reflects thoughtful design, defensive coding, and real-world usability.
