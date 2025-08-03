import meraki

API_Key = '14ae6db50c95a7c2bcdab9b9e2871f61d7fb4a48'
ORGANIZATION_ID = '641762946900418947'


dashboard = meraki.DashboardAPI(API_Key)


response = dashboard.organizations.getOrganizationNetworks(ORGANIZATION_ID)

# Prompt user for action, type, and value
action = input("Do you want to add or remove a rule? (add/remove): ").strip().lower()
rule_type = input("Enter the rule type (host, port, applicationCategory, etc.): ").strip()
rule_value = input("Enter the value for the rule (e.g., google.com, 443, etc.): ").strip()

for network in response:
    if 'appliance' not in network.get('productTypes', []):
        continue
    network_id = network['id']
    try:
        # Get current Layer 7 firewall rules
        rules_resp = dashboard.appliance.getNetworkApplianceFirewallL7FirewallRules(network_id)
        l7_rules = rules_resp.get('rules', [])

        if action == "add":
            new_rule = {
                'policy': 'deny',
                'type': rule_type,
                'value': rule_value
            }
            l7_rules.append(new_rule)
            dashboard.appliance.updateNetworkApplianceFirewallL7FirewallRules(
                network_id,
                rules=l7_rules
            )
            print(f"Added rule to {network_id}: {new_rule}")
        elif action == "remove":
            # Remove matching rules
            filtered_rules = [r for r in l7_rules if not (r.get('type') == rule_type and str(r.get('value')) == rule_value)]
            dashboard.appliance.updateNetworkApplianceFirewallL7FirewallRules(
                network_id,
                rules=filtered_rules
            )
            print(f"Removed rule from {network_id}: type={rule_type}, value={rule_value}")
        else:
            print(f"Invalid action: {action}. Skipping network {network_id}.")
    except Exception as e:
        print(f"Error with network {network_id}: {e}")