import os
import ipinfo
from dotenv import load_dotenv
from user_agents import parse

load_dotenv()
IPINFO_API_KEY = os.getenv("IPINFO_API_KEY")

# get user ip address and country
# Update get_ip to accept the request
def get_ip(request):
    client_ip = request.headers.get("X-Forwarded-For")
    
    if not client_ip:
        client_ip = request.client.host
    
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()
    
    handler = ipinfo.getHandler(access_token=IPINFO_API_KEY)
    details = handler.getDetails(client_ip)
    
    # Debug: print what's available
    print(f"Details all: {details.all}")
    print(f"Available keys: {details.all.keys()}")
    
    # Try to get country from the dict
    country = details.all.get("country_name") or details.all.get("country") or "Unknown"
    
    return {
        "ip_address": details.all.get("ip", client_ip),
        "country": country
    }

# get device type
def get_device_type(request):
    agent = request.headers.get("user-agent")
    if agent:
        user_agent = parse(agent)

        if user_agent.is_mobile:
            return "Mobile"
        if user_agent.is_tablet:
            return "Tablet"
        if user_agent.is_pc:
            return "Desktop"
        else:
            return "Other"
        
    return "Unknown Device"

