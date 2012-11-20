# Your project must provide non-null values for these HealthVault access
# credentials:
HEALTHVAULT_APP_ID = None
HEALTHVAULT_THUMBPRINT = None
HEALTHVAULT_PUBLIC_KEY = None
HEALTHVAULT_PRIVATE_KEY = None
HEALTHVAULT_SERVER = None
HEALTHVAULT_SHELL_SERVER = None

# Where to redirect to after successful completion of HealthVault integration.
HEALTHVAULT_AUTHORIZE_REDIRECT = '/'

# Where to redirect to after removal of HealthVault credentials.
HEALTHVAULT_DEAUTHORIZE_REDIRECT = '/'

# The template to use when an unavoidable error occurs during HealthVault
# integration.
HEALTHVAULT_ERROR_TEMPLATE = 'healthvaultapp/error.html'
