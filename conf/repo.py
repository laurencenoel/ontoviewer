from pyramid.config import Configurator
from pyramid.threadlocal import get_current_registry

registry = get_current_registry()
settings = registry.settings
if settings == None :
    import configparser
    config = configparser.ConfigParser()
    config.read('../development.ini')
    settings=config['app:main']

HCAOQUERY = settings['repo_hcao_query']
HCAOUPDATE = settings['repo_hcao_update']
MONDOQUERY = settings['repo_mondo_query']
EHDAAQUERY = settings['repo_ehdaa_query']

STR_HCAO = "http://purl.obolibrary.org/obo/"
