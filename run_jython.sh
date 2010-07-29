#
# To run in jython make sure that  you have
# * the genlib/python folder in your $JYTHONPATH (just like you would with C-python)
# * a JDBC postgres driver in your $CLASSPATH
#
# Also, all the standard crawl dependencies apply, which can all be installed with a 
# jython easy_install, with one exception : you need to install a CherryPy-3.2.0rc1 
# at the very least, because there is a bug in the 3.1 version that causes exceptuions 
# when trying to access threading properties. 
# 

jython -Dlogfolder=/tmp server.py -c ini/config.py -l ini/logging.ini #-p /home/gv1/tmp/pid -d -t

