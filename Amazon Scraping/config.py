from operator import concat
import os

# Obtenez le chemin absolu du répertoire contenant votre fichier courant
current_dir = os.path.dirname(os.path.abspath(__file__))

# URL variables
AMAZON_URL = 'https://www.amazon.com'
BASE_URL = 'https://example.com'

# Driver variables 
CHROME_DRIVER = concat(current_dir,'Divers/Chrome Driver/chromedriver.exe').replace("\\", "/")

# Identification variables 
USERNAME = 'your_username'
PASSWORD = 'your_password'