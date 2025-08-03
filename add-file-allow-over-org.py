import meraki

API_Key = '14ae6db50c95a7c2bcdab9b9e2871f61d7fb4a48'
ORGANIZATION_ID = '641762946900418947'


dashboard = meraki.DashboardAPI(API_Key)

response = dashboard.organizations.getOrganizationNetworks(ORGANIZATION_ID)
