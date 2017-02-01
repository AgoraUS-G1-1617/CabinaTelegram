from pybuilder.core import use_plugin, init, Author

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")


summary = 'Proyecto de EGC del grupo de Cabina de Votación Telegram para el curso 2016-2017 por la ETSII'
authors = (Author('Jorge Puente Zaro'), Author('Jose Luis Salazar González'), Author('Jose Manuel Gavira González'), Author('Juan Rodríguez Dueñas'))
url = 'https://github.com/AgoraUS-G1-1617/CabinaTelegram'

default_task = "publish"

@init
def initialize(project):
    project.set_property("version", '1.1')
    project.depends_on_requirements("requirements.txt")
    project.version = project.get_property("version")
