from msal import PublicClientApplication
import requests
from datetime import datetime, timedelta
# El objetivo de este script es de activar los recursos de Azure. 
# Al final no se ha podido lograr:  
# Los permisos de Azure para habilitar recursos no son fáciles. 



app = PublicClientApplication("YOUR_CLIENT_ID", 
        authority="https://login.microsoftonline.com/YOUR_TENANT_ID")
scopes = ["https://graph.microsoft.com/.default"]

result = app.acquire_token_interactive(scopes=scopes)

token = result["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "principalId": "USER_OBJECT_ID",
    "roleDefinitionId": "ROLE_ID",
    "directoryScopeId": "/",
    "action": "SelfActivate",
    "justification": "Need access",
    "scheduleInfo": {
        "startDateTime": datetime.utcnow().isoformat() + "Z",
        "expiration": {
            "type": "AfterDuration",
            "duration": "PT4H"
        }
    }
}

response = requests.post(
    "https://graph.microsoft.com/v1.0/roleManagement/directory/roleEligibilityScheduleRequests",
    headers=headers,
    json=payload
)

print(response.status_code, response.text)