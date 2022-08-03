import os
import dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
	dotenv.load_dotenv(dotenv_file)

if os.environ['ENV_TYPE'] == 'prod':
	from . prod import *

elif os.environ['ENV_TYPE'] == 'dev':
	from . dev import *

else:
	raise Exception('Invalid ENV_TYPE, please set <dev> or <prod> in .env.')
