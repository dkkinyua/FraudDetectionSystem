import os
import ipinfo
from dotenv import load_dotenv
from user_agents import parse

load_dotenv()
IPINFO_API_KEY = os.getenv("IPINFO_API_KEY")

# get user ip address and country
def get_ip():
    handler = ipinfo.HandlerLite(access_token=IPINFO_API_KEY)
    details = handler.getDetails()

    return {
        "ip_address": details.ip,
        "country": details.country
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

