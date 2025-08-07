import meraki
import getpass

# Replace with your actual API key and Org ID
API_Key = '14ae6db50c95a7c2bcdab9b9e2871f61d7fb4a48'
ORGANIZATION_ID = '641762946900418947'

# Prompt for new credentials
username = input('Enter new local credentials username: ')
password = getpass.getpass('Enter new local credentials password: ')

# Initialize Meraki Dashboard API
dashboard = meraki.DashboardAPI(API_Key, suppress_logging=True)

# Get all networks in the organization
networks = dashboard.organizations.getOrganizationNetworks(ORGANIZATION_ID)

# Filter for SD-WAN (appliance) networks
appliance_networks = [n for n in networks if 'appliance' in n.get('productTypes', [])]

print(f'Found {len(appliance_networks)} SD-WAN (appliance) networks.')

# Update local status page credentials for each network
for net in appliance_networks:
    try:
        dashboard.networks.updateNetworkSettings(
            net['id'],
            localStatusPage={
                "authentication": {
                    "enabled": True,
                    "username": username,
                    "password": password
                }
            }
        )
        print(f"✅ Updated credentials for network: {net['name']} ({net['id']})")
    except Exception as e:
        print(f"❌ Failed to update {net['name']} ({net['id']}): {e}")

