from novaclient import client
nova = client.Client(2, "admin", PASSWORD, PROJECT_ID, AUTH_URL)
