import os
import ipinfo
from dotenv import load_dotenv
from user_agents import parse

load_dotenv()
IPINFO_API_KEY = os.getenv("IPINFO_API_KEY")

# get user ip address and country
# Update get_ip to accept the request
def get_ip(request):
    # Get client IP from request headers
    # Render, in prod, passes the real IP in X-Forwarded-For
    client_ip = request.headers.get("X-Forwarded-For", request.client.host)
    
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()
    
    handler = ipinfo.HandlerLite(access_token=IPINFO_API_KEY)
    details = handler.getDetails(client_ip)
    
    return {
        "ip_address": details.ip,
        "country": details.country_name
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

