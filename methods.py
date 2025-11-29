
import os
import json
import logging
from datetime import datetime, timedelta, UTC
from dateutil.parser import parse as dparse
import requests
from dotenv import load_dotenv
import pytz

IST = pytz.timezone("Asia/Kolkata")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("projects_monitor")

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, 'config.env'), override=True)


CLIENT_ID        = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET    = os.getenv("ZOHO_CLIENT_SECRET")
REFRESH_TOKEN    = os.getenv("ZOHO_REFRESH_TOKEN")
PORTAL_NAME      = os.getenv("PORTAL_NAME", "mohansaradygmaildotcom")
PROJECT_ID       = os.getenv("PROJECT_ID")
REGION           = os.getenv("REGION", "in")
DUE_SOON_HOURS   = int(os.getenv("DUE_SOON_HOURS", "24"))
'''
print("===== ENV CHECK =====")
print("CLIENT_ID:", CLIENT_ID)
print("CLIENT_SECRET:", CLIENT_SECRET)
print("REFRESH_TOKEN:", REFRESH_TOKEN)
print("REGION:", REGION)
print("PORTAL NAME:", PORTAL_NAME)
print("PROJECT ID:", PROJECT_ID)
print("======================")

'''

# Region-specific endpoints
if REGION.lower() == "in":
    OAUTH_URL = "https://accounts.zoho.in/oauth/v2/token"
    PROJECTS_API_BASE = f"https://projectsapi.zoho.in/restapi/portal/{PORTAL_NAME}"
    CLIQ_API_BASE = "https://cliq.zoho.in/api/v2"
else:
    OAUTH_URL = "https://accounts.zoho.com/oauth/v2/token"
    PROJECTS_API_BASE = f"https://projectsapi.zoho.com/restapi/portal/{PORTAL_NAME}"
    CLIQ_API_BASE = "https://cliq.zoho.com/api/v2"

# token cache
TOKEN_CACHE = {"access_token": None, "expires_at": None}

# ---------- get fresh access token ----------
def refresh_access_token():
    now = datetime.now(UTC)

    if TOKEN_CACHE["access_token"] and TOKEN_CACHE["expires_at"] > now:
        return TOKEN_CACHE["access_token"]

    payload = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }

    r = requests.post(OAUTH_URL, data=payload)
    r.raise_for_status()
    data = r.json()

    token = data["access_token"]
    expires_in = int(data.get("expires_in", 3600))

    TOKEN_CACHE["access_token"] = token
    TOKEN_CACHE["expires_at"] = now + timedelta(seconds=expires_in)

    log.info("Refreshed access token; expires in %s seconds", expires_in)
    return token

# ---------- helpers ----------
def zoho_get(url, params=None):
    t = refresh_access_token()
    headers = {"Authorization": "Zoho-oauthtoken " + t}
    r = requests.get(url, headers=headers, params=params)

    # DEBUG LOGGING
    '''
    print("===== ZOHO GET DEBUG =====")
    print("URL:", url)
    print("Params:", params)
    print("Status Code:", r.status_code)
    print("Raw Response Text:", r.text)
    print("==========================")
    '''
    r.raise_for_status()
    return r.json()

def zoho_post(url, body, extra_headers=None):
    token = refresh_access_token()
    headers = {
        "Authorization": "Zoho-oauthtoken " + token,
        "Content-Type": "application/json"
    }
    if extra_headers:
        headers.update(extra_headers)
    resp = requests.post(url, headers=headers, json=body)

    # DEBUG LOGGING for POST
    '''
    print("===== ZOHO POST DEBUG =====")
    print("URL:", url)
    print("Body:", body)
    print("Status Code:", resp.status_code)
    print("Raw Response Text:", resp.text)
    print("==========================")
    '''

    resp.raise_for_status()
    return resp.json()

def safe_iter(obj):
    return isinstance(obj, (list, tuple))

def parse_due_date(task):
    try:
        end_format = task.get("end_date_format") or task.get("end_date_time") or task.get("due_date_time")
        if end_format:
            return dparse(end_format)

        if task.get("end_date_long"):
            ms = int(task["end_date_long"])
            return datetime.fromtimestamp(ms / 1000.0, tz=pytz.UTC).astimezone(IST)

        if task.get("end_date"):
            return dparse(task["end_date"])
    except Exception as ex:
        print("Could not parse due date:", ex)
        return None

def send_dm_to_owner(owner_email, message_text):
    try:
        cliq_lookup = zoho_get(f"{CLIQ_API_BASE}/users", params={"search": owner_email})
        data = cliq_lookup.get("data", [])
        if not safe_iter(data) or not data:
            return False

        user_entry = data[0]
        buddy_id = user_entry.get("zuid") or user_entry.get("email_id") or user_entry.get("id")
        if not buddy_id:
            return False

        token = refresh_access_token()
        headers = {"Authorization": "Zoho-oauthtoken " + token, "Content-Type": "application/json"}
        body = {"text": message_text}
        resp = requests.post(f"{CLIQ_API_BASE}/buddies/{buddy_id}/message", headers=headers, json=body)

        if "buddies_self_message_restricted" in resp.text:
            print("Info: cannot send DM to self for owner:", owner_email)
            return False

        resp.raise_for_status()
        return True
    except Exception as e:
        log.exception("Error sending DM to %s", owner_email)
        return False
# ---------- core logic ----------
def process_tasks_and_notify():
    result = {"checked": 0, "alerts_sent": 0, "alerts": []}

    try:
        url = f"{PROJECTS_API_BASE}/projects/{PROJECT_ID}/tasks/"
        resp = zoho_get(url)
    except Exception as e:
        log.exception("Error fetching tasks")
        return {"error": "Fetch failed", "detail": str(e)}

    tasks = resp.get("tasks", [])
    if not safe_iter(tasks):
        return {"error": "Invalid task format", "raw": resp}

    now = datetime.now(IST)
    cutoff = now + timedelta(hours=DUE_SOON_HOURS)

    for t in tasks:
        try:
            result["checked"] += 1
            name = t.get("name", "Unnamed Task")
            percent = int(t.get("percent_complete") or 0)
            due = parse_due_date(t)

            if due and due.tzinfo is None:
                due = IST.localize(due)

            is_due_soon = due and due < cutoff
            is_overdue = due and due < now

            if not due or percent == 100 or (not is_due_soon and not is_overdue):
                continue

            label = "⚠️ OVERDUE" if is_overdue else "🚨 DUE SOON"
            message_text = f"{label} - Task *{name}* is at risk!\nCompletion: {percent}%\nDue: {due.strftime('%Y-%m-%d %I:%M %p')} (IST)"

            # Extract owners
            owners_to_notify = []
            details = t.get("details") or {}
            details_owners = details.get("owners") if isinstance(details, dict) else None
            if isinstance(details_owners, (list, tuple)) and details_owners:
                owners_to_notify = details_owners[:]
            else:
                ol = t.get("owners") or t.get("owner") or t.get("assigned_to")
                if isinstance(ol, list):
                    owners_to_notify = ol[:]
                elif isinstance(ol, dict):
                    owners_to_notify = [ol]
                elif ol:
                    owners_to_notify = [{"id": ol}]

            for owner_obj in owners_to_notify:
                try:
                    if not isinstance(owner_obj, dict):
                        owner_obj = {"id": owner_obj}

                    owner_email = owner_obj.get("email") or owner_obj.get("email_id") or owner_obj.get("user_email") or owner_obj.get("created_by_email")
                    if not owner_email:
                        continue

                    if send_dm_to_owner(owner_email, message_text):
                        result["alerts_sent"] += 1
                        result["alerts"].append({"task": name, "user": owner_email})
                except Exception as e:
                    log.exception("Error processing owner: %s", e)
                    continue

        except Exception as e:
            log.exception("Error processing task: %s", e)

    return result

    
def generate_daily_digest():
    try:
        url = f"{PROJECTS_API_BASE}/projects/{PROJECT_ID}/tasks/"
        resp = zoho_get(url)
    except Exception as e:
        log.exception("Error fetching tasks for digest")
        return {"error": "Fetch failed", "detail": str(e)}

    tasks = resp.get("tasks", [])
    if not safe_iter(tasks):
        return {"error": "Invalid task format", "raw": resp}

    now = datetime.now(IST)
    cutoff = now + timedelta(hours=DUE_SOON_HOURS)

    digest_lines = []
    owners_to_notify = set()

    for t in tasks:
        name = t.get("name", "Unnamed Task")
        percent = int(t.get("percent_complete") or 0)

        # parse due date (same as in process_tasks_and_notify)
        due = None
        end_format = t.get("end_date_format") or t.get("end_date_time") or t.get("due_date_time")
        if end_format:
            due = dparse(end_format)
        elif t.get("end_date_long"):
            ms = int(t["end_date_long"])
            due = datetime.fromtimestamp(ms / 1000.0, tz=pytz.UTC).astimezone(IST)
        elif t.get("end_date"):
            due = dparse(t["end_date"])
        if due and due.tzinfo is None:
            due = IST.localize(due)

        is_due_soon = due and due < cutoff
        is_overdue = due and due < now
        if not due or percent == 100 or (not is_due_soon and not is_overdue):
            continue

        label = "⚠️ OVERDUE" if is_overdue else "🚨 DUE SOON"
        digest_lines.append(f"{label} *{name}* — {percent}% complete, due {due.strftime('%Y-%m-%d %I:%M %p')}")

        # collect owners
        details = t.get("details") or {}
        details_owners = details.get("owners") if isinstance(details, dict) else None
        if isinstance(details_owners, (list, tuple)):
            for o in details_owners:
                if isinstance(o, dict) and o.get("email"):
                    owners_to_notify.add(o.get("email"))

    digest_text = f"*Daily Risk Digest — {now.strftime('%Y-%m-%d %I:%M %p')} IST*\n" + "\n".join(digest_lines)

    sent_count = 0
    for email in owners_to_notify:
        if send_dm_to_owner(email, digest_text):
            sent_count += 1

    return {"status": "ok", "digest_sent": sent_count, "owners": list(owners_to_notify)}