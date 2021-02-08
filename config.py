#!/usr/bin/python
"""config.py: Funcion para obtener los parametros de conexion del archivo "database.ini" """
__author__ = "Ana María Manso Rodríguez"
__credits__ = ["Ana María Manso Rodríguez"]
__version__ = "1.0"
__status__ = "Development"

from configparser import ConfigParser


def config(filename='database.ini', section='mariadb'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to mariadb
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
            if param[0] == 'port':
                db[param[0]] = int(param[1])
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
