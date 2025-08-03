import meraki

API_Key = '14ae6db50c95a7c2bcdab9b9e2871f61d7fb4a48'
ORGANIZATION_ID = '641762946900418947'


dashboard = meraki.DashboardAPI(API_Key)

response = dashboard.organizations.getOrganizationNetworks(ORGANIZATION_ID)

# Prompt user for action and URL

# Prompt user for list type, action, and URL
list_type = input("Which list do you want to modify? (allow/block): ").strip().lower()
action = input("Do you want to add or remove a URL? (add/remove): ").strip().lower()
target_url = input("Enter the URL to add or remove: ").strip()



for network in response:
    # Only process MX networks
    if 'appliance' not in network.get('productTypes', []):
        continue
    network_id = network['id']
    try:
        # Get current content filtering settings
        settings = dashboard.appliance.getNetworkApplianceContentFiltering(network_id)
        allowed_urls = settings.get('allowedUrlPatterns', [])
        blocked_urls = settings.get('blockedUrlPatterns', [])

        if list_type == "allow":
            url_list = allowed_urls
            field_name = 'allowedUrlPatterns'
        elif list_type == "block":
            url_list = blocked_urls
            field_name = 'blockedUrlPatterns'
        else:
            print(f"Invalid list type: {list_type}. Skipping network {network_id}.")
            continue

        if action == "add":
            if target_url not in url_list:
                url_list.append(target_url)
        elif action == "remove":
            url_list = [url for url in url_list if url != target_url]
        else:
            print(f"Invalid action: {action}. Skipping network {network_id}.")
            continue

        # Apply changes to both uplinks
        for uplink in ["wan1", "wan2"]:
            update_payload = {field_name: url_list, 'uplink': uplink}
            try:
                dashboard.appliance.updateNetworkApplianceContentFiltering(
                    network_id,
                    **update_payload
                )
                print(f"{action.capitalize()}ed {target_url} in {list_type} list for network {network_id} on {uplink}")
            except Exception as e:
                print(f"Error with network {network_id} on {uplink}: {e}")
    except Exception as e:
        print(f"Error with network {network_id}: {e}")