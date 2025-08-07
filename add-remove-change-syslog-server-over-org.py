import meraki

API_Key = '14ae6db50c95a7c2bcdab9b9e2871f61d7fb4a48'
ORGANIZATION_ID = '641762946900418947'

dashboard = meraki.DashboardAPI(API_Key, suppress_logging=True)

# Get all appliance networks
networks = dashboard.organizations.getOrganizationNetworks(ORGANIZATION_ID)
appliance_networks = [n for n in networks if 'appliance' in n.get('productTypes', [])]

print(f'Found {len(appliance_networks)} SD-WAN (appliance) networks.')

# Choose action
action = input("Choose action: [add] Add new syslog, [remove] Remove by IP, [change] Modify existing by IP: ").strip().lower()

if action in ['add', 'change']:
    target_ip = input("Enter IP of the syslog server to add or modify: ").strip()
    server_port = int(input("Enter syslog server port (e.g., 514): "))
    roles = input("Enter roles ('appliance event log, urls,flows'): ").split(',')

    new_server = {
        "host": target_ip,
        "port": server_port,
        "roles": [r.strip() for r in roles]
    }

elif action == 'remove':
    target_ip = input("Enter IP of the syslog server to remove from all networks: ").strip()

for net in appliance_networks:
    try:
        current = dashboard.networks.getNetworkSyslogServers(net['id'])
        servers = current.get('servers', [])

        if action == 'remove':
            updated_servers = [s for s in servers if s['host'] != target_ip]

            if len(servers) == len(updated_servers):
                print(f"ℹ️ No matching syslog server found in {net['name']}")
            else:
                dashboard.networks.updateNetworkSyslogServers(net['id'], servers=updated_servers)
                print(f"🗑️ Removed syslog server {target_ip} from {net['name']}")

        elif action == 'add':
            updated_servers = servers + [new_server]
            dashboard.networks.updateNetworkSyslogServers(net['id'], servers=updated_servers)
            print(f"➕ Added syslog server to {net['name']}")

        elif action == 'change':
            updated_servers = []
            found = False
            for s in servers:
                if s['host'] == target_ip:
                    updated_servers.append(new_server)
                    found = True
                else:
                    updated_servers.append(s)

            if not found:
                print(f"ℹ️ No matching syslog server found in {net['name']}")
            else:
                dashboard.networks.updateNetworkSyslogServers(net['id'], servers=updated_servers)
                print(f"🔄 Updated syslog server {target_ip} in {net['name']}")

    except Exception as e:
        print(f"❌ Failed on {net['name']} ({net['id']}): {e}")


