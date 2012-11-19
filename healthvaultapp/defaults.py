# Your project must provide the following HealthVault app access credentials:
#   HEALTHVAULT_APP_ID
#   HEALTHVAULT_THUMBPRINT
#   HEALTHVAULT_PUBLIC_KEY
#   HEALTHVAULT_PRIVATE_KEY
#   HEALTHVAULT_SHELL_SERVER

# Where to redirect to after successful completion of HealthVault integration.
HEALTHVAULT_AUTHORIZE_REDIRECT = '/'

# Where to redirect to after removal of HealthVault credentials.
HEALTHVAULT_DEAUTHORIZE_REDIRECT = '/'

# The template to use when an unavoidable error occurs during HealthVault
# integration.
HEALTHVAULT_ERROR_TEMPLATE = 'healthvaultapp/error.html'
