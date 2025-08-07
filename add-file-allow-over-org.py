import meraki
import sys

#THIS SCRIPT MAY NEED AMP ENABLED PRIOR TO RUNNING, CAN'T SEEM TO GET IT TO ENABLE VIA THE API AND CAN'T TEST

# Replace with your actual API key and organization ID
API_Key = '14ae6db50c95a7c2bcdab9b9e2871f61d7fb4a48'
ORGANIZATION_ID = '641762946900418947'

dashboard = meraki.DashboardAPI(API_Key, suppress_logging=True)

# Prompt user for action and file details
action = input("Do you want to add or remove a file allow entry? (add/remove): ").strip().lower()
if action not in ["add", "remove"]:
    print(f"❌ Invalid action: {action}. Exiting.")
    sys.exit()

sha256 = input("Enter the SHA256 hash of the file: ").strip()
comment = input("Enter a comment for this file entry: ").strip()

# Get all networks in the organization
networks = dashboard.organizations.getOrganizationNetworks(ORGANIZATION_ID)

for network in networks:
    if 'appliance' not in network.get('productTypes', []):
        continue

    network_id = network['id']
    try:
        amp_settings = dashboard.appliance.getNetworkApplianceSecurityMalware(network_id)

        # Always set mode to 'enabled'
        mode = 'enabled'
        allowed_files = amp_settings.get('allowedFiles', [])
        allowed_urls = amp_settings.get('allowedUrls', [])

        if action == 'add':
            if any(f['sha256'] == sha256 for f in allowed_files):
                print(f"⚠️ File with SHA256 '{sha256}' already allowed in {network['name']}. Skipping.")
                continue
            allowed_files.append({'sha256': sha256, 'comment': comment})

        elif action == 'remove':
            if not any(f['sha256'] == sha256 for f in allowed_files):
                print(f"⚠️ File with SHA256 '{sha256}' not found in {network['name']}. Skipping.")
                continue
            allowed_files = [f for f in allowed_files if f['sha256'] != sha256]

        # Update AMP settings
        dashboard.appliance.updateNetworkApplianceSecurityMalware(
            network_id,
            mode,
            allowedUrls=allowed_urls,
            allowedFiles=allowed_files
        )
        print(f"✅ {action.capitalize()}ed file SHA256 '{sha256}' in network: {network['name']}")

    except Exception as e:
        print(f"❌ Error updating {network['name']} ({network_id}): {e}")
