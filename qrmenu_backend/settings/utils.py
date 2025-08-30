import os


def get_current_environment():

	"""
	1. Set environment to PRODUCTION ENVIRONMENT.
	2. Check if environment variables are working.
	3. If env variables aren't working, we are in DEVELOPMENT.
	4. Change to DEVELOPMENT ENVIRONMENT.
	"""

	AVAILABLE_ENVIRONMENTS = ['DEVELOPMENT', 'PRODUCTION']

	# Production
	environment = str(os.environ.get("ENVIRONMENT"))
	
	# Development
	if environment not in AVAILABLE_ENVIRONMENTS:

		from dotenv import load_dotenv
		load_dotenv()
		environment = os.getenv('ENVIRONMENT')

	return environment