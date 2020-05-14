from pyramid.config import Configurator
from pyramid.threadlocal import get_current_registry
from repoConf import *

registry = get_current_registry()
settings = registry.settings
if settings == None :
    import configparser
    config = configparser.ConfigParser()
    config.read('development.ini')
    settings=config['app:main']

HCAOQUERY = settings['repo_hcao_query']
HCAOUPDATE = settings['repo_hcao_update']
MONDOQUERY = settings['repo_mondo_query']
