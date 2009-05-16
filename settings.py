# import everything from rapidsms
from rapidsms.webui.settings import *
# now do overrides

# add in rapidsms_baseui
INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.append('malnutrition.ui')