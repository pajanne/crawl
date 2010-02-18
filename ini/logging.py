[loggers]
keys=root,charpy,ropy

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler,fileHandler

[logger_ropy]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname=ropy
propagate=0

[logger_charpy]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname=charpy
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=handlers.RotatingFileHandler
level=DEBUG
formatter=simpleFormatter
args=('/Users/gv1/tmp/charpy.log', 'a', 5000000, 5)

[formatter_simpleFormatter]
format= [%(levelname)s] - %(thread)d - [%(name)s] %(pathname)s,%(lineno)d %(funcName)s()  - %(message)s
datefmt=

