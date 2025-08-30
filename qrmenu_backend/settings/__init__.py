import os
from .utils import get_current_environment

ENVIRONMENT = get_current_environment()

print("ENVIRONMENT: ", ENVIRONMENT)

from .base import *
    

if ENVIRONMENT == 'DEVELOPMENT':
    from .dev import *
else:
    from .prod import *