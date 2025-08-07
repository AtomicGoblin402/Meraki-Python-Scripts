import meraki

API_Key = '14ae6db50c95a7c2bcdab9b9e2871f61d7fb4a48'
ORGANIZATION_ID = '641762946900418947'

dashboard = meraki.DashboardAPI(API_Key, suppress_logging=True)

# Get all networks
networks = dashboard.organizations.getOrganizationNetworks(ORGANIZATION_ID)

# Choose action
action = input("Choose action: [add] Add user, [remove] Remove user by username, [change] Modify user: ").strip().lower()

if action == 'add':
    username = input("Enter new SNMP v3 username: ").strip()
    password = input("Enter new SNMP v3 password: ").strip()
    new_user = {"username": username, "passphrase": password}

elif action == 'remove':
    target_username = input("Enter SNMP v3 username to remove from all networks: ").strip()

elif action == 'change':
    target_username = input("Enter SNMP v3 username to modify: ").strip()
    change_name = input("Do you want to change the username? (yes/no): ").strip().lower()
    new_username = input("Enter new username: ").strip() if change_name == 'yes' else target_username
    new_password = input("Enter new password: ").strip()
    updated_user = {"username": new_username, "passphrase": new_password}

# Apply changes to each network
for net in networks:
    try:
        network_id = net['id']
        snmp_config = dashboard.networks.getNetworkSnmp(network_id)

        # Ensure communityString is a valid string
        community_string = snmp_config.get('communityString')
        if not isinstance(community_string, str):
            community_string = "sample"  # fallback default

        users = snmp_config.get('users', [])

        if action == 'add':
            users.append(new_user)

        elif action == 'remove':
            users = [u for u in users if u['username'] != target_username]

        elif action == 'change':
            found = False
            new_list = []
            for user in users:
                if user['username'] == target_username:
                    new_list.append(updated_user)
                    found = True
                else:
                    new_list.append(user)
            if not found:
                print(f"❌ No user '{target_username}' found in {net['name']}")
                continue
            users = new_list

        # Update SNMP settings with access='users' to enable SNMPv3
        response = dashboard.networks.updateNetworkSnmp(
            network_id,
            access='users',
            communityString=community_string,
            users=users
        )
        print(f"✅ SNMP v3 updated for network: {net['name']}")

    except Exception as e:
        print(f"❌ Failed on {net['name']} ({net['id']}): {e}")
