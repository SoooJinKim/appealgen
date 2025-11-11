# api_diagnose_en.py
from openai import OpenAI
import os
import requests

def check_openai_environment():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("❌ Environment variable OPENAI_API_KEY is not set.")
        print('   → In PowerShell, run:  setx OPENAI_API_KEY "sk-..."')
        return None
    if not key.startswith("sk-"):
        print("⚠️  API key format looks incorrect (it should start with 'sk-').")
    return key

def check_organization(client):
    try:
        org = client.organization
        print(f"✅ Organization ID: {org if org else 'Personal account (organization=None)'}")
    except Exception as e:
        print(f"❌ Failed to fetch organization info: {e}")

def check_models(client):
    try:
        models = [m.id for m in client.models.list().data]
        print(f"✅ Accessible models: {len(models)} found")
        for m in models[:10]:
            print(f"   - {m}")
        if not any("gpt" in m for m in models):
            print("⚠️  No GPT models detected. Access may be limited.")
    except Exception as e:
        print(f"❌ Failed to list models: {e}")

def test_model_access(client):
    print("\n🧠 Testing model access (gpt-4o-mini → gpt-3.5-turbo fallback)")
    for model in ["gpt-4o-mini", "gpt-3.5-turbo"]:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Testing if this API key can call the model."}],
                max_tokens=10,
            )
            print(f"✅ {model}: call succeeded → {resp.choices[0].message.content}")
            return True
        except Exception as e:
            print(f"❌ {model}: {e}")
    print("⚠️  Both models failed → likely quota issue or billing inactive.")
    return False

def check_quota_status(api_key):
    """Indirectly checks billing/quota info using the dashboard endpoint."""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        url = "https://api.openai.com/dashboard/billing/subscription"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            print("\n💰 Billing / Credit Info")
            plan = data.get("plan", {}).get("title", "N/A")
            soft_limit = data.get("soft_limit_usd", 0)
            hard_limit = data.get("hard_limit_usd", 0)
            print(f"   - Plan: {plan}")
            print(f"   - Credit limit: ${soft_limit:.2f} (max ${hard_limit:.2f})")
            print(f"   - Billing active: {'✅ Yes' if hard_limit > 0 else '❌ No'}")
        else:
            print(f"⚠️  Billing API request failed: HTTP {resp.status_code}")
    except Exception as e:
        print(f"⚠️  Could not check billing info: {e}")

if __name__ == "__main__":
    print("🔍 Diagnosing OpenAI API environment...\n")

    key = check_openai_environment()
    if not key:
        exit()

    client = OpenAI(api_key=key)

    check_organization(client)
    print()
    check_models(client)
    test_model_access(client)
    check_quota_status(key)

    print("\n✅ Diagnosis completed.")
