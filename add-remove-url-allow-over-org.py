import meraki
import sys

# Replace with your actual API key and organization ID
API_Key = '14ae6db50c95a7c2bcdab9b9e2871f61d7fb4a48'
ORGANIZATION_ID = '641762946900418947'

dashboard = meraki.DashboardAPI(API_Key, suppress_logging=True)

# Prompt user for list type, action, and URL
list_type = input("Which list do you want to modify? (allow/block): ").strip().lower()
if list_type not in ["allow", "block"]:
    print(f"❌ Invalid list type: {list_type}. Exiting.")
    sys.exit()

action = input("Do you want to add or remove a URL? (add/remove): ").strip().lower()
if action not in ["add", "remove"]:
    print(f"❌ Invalid action: {action}. Exiting.")
    sys.exit()

target_url = input("Enter the URL to add or remove: ").strip()

# Get all networks in the organization
networks = dashboard.organizations.getOrganizationNetworks(ORGANIZATION_ID)

for network in networks:
    if 'appliance' not in network.get('productTypes', []):
        continue

    network_id = network['id']
    try:
        # Get current content filtering settings
        settings = dashboard.appliance.getNetworkApplianceContentFiltering(network_id)

        allowed_urls = settings.get('allowedUrlPatterns', [])
        blocked_urls = settings.get('blockedUrlPatterns', [])
        blocked_categories = settings.get('blockedUrlCategories', [])
        category_list_size = settings.get('urlCategoryListSize', 'topSites')

        if list_type == "allow":
            url_list = allowed_urls
            field_name = 'allowedUrlPatterns'
        else:
            url_list = blocked_urls
            field_name = 'blockedUrlPatterns'

        # Modify the list
        if action == "add":
            if target_url in url_list:
                print(f"⚠️ URL '{target_url}' already exists in {list_type} list for network: {network['name']}. Skipping.")
                continue
            url_list.append(target_url)
        elif action == "remove":
            if target_url not in url_list:
                print(f"⚠️ URL '{target_url}' not found in {list_type} list for network: {network['name']}. Skipping.")
                continue
            url_list = [url for url in url_list if url != target_url]

        # Build update payload
        update_payload = {
            'allowedUrlPatterns': allowed_urls,
            'blockedUrlPatterns': blocked_urls,
            'blockedUrlCategories': blocked_categories,
            'urlCategoryListSize': category_list_size
        }

        # Apply update
        dashboard.appliance.updateNetworkApplianceContentFiltering(
            network_id,
            **update_payload
        )

        print(f"✅ {action.capitalize()}ed '{target_url}' in {list_type} list for network: {network['name']}")

    except Exception as e:
        print(f"❌ Error updating {network['name']} ({network_id}): {e}")
