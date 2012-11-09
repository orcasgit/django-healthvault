# Your project must provide the following HealthVault app access credentials:
#   HEALTHVAULT_APP_ID
#   HEALTHVAULT_THUMBPRINT
#   HEALTHVAULT_PUBLIC_KEY
#   HEALTHVAULT_PRIVATE_KEY

# This is the pre-production server for the US.
HEALTHVAULT_SHELL_SERVER = 'account.healthvault-ppe.com'

# Where to redirect to after HealthVault authentication is successfully
# completed.
HEALTHVAULT_LOGIN_REDIRECT = '/'

# Where to redirect to after HealthVault authentication credentials have been
# removed.
HEALTHVAULT_LOGOUT_REDIRECT = '/'

# The template to use when an unavoidable error occurs during HealthVault
# integration.
HEALTHVAULT_ERROR_TEMPLATE = 'healthvaultapp/error.html'
