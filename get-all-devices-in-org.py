import meraki
import pandas as pd

# Replace with your actual API key and organization ID
API_KEY = '14ae6db50c95a7c2bcdab9b9e2871f61d7fb4a48'
ORGANIZATION_ID = '641762946900418947'

# Initialize Meraki dashboard API
dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)

# Get all devices in the organization
devices = dashboard.organizations.getOrganizationDevices(
    ORGANIZATION_ID, total_pages='all'
)

# Convert the list of devices to a DataFrame
df = pd.DataFrame(devices)

# Save the DataFrame to an Excel file
df.to_excel('meraki_devices.xlsx', index=False)

print(f"✅ Exported {len(devices)} devices to 'meraki_devices.xlsx'")
