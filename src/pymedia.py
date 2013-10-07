#!/bin/python

import	ctypes
import	logging
import	os
import	re
import	sys

sys.setrecursionlimit(5000)
###------------------------------------------------------------------------------------------------------------------------------
def argparser():
	import argparse
	
	global Logger
	ap = argparse.ArgumentParser( description = 'A pythonized front end to MediaInfo.', prog = os.path.basename(re.sub(".py", "", sys.argv[0])) )
	gap = ap.add_argument_group( 'program information' )
	gap.add_argument( 		'--version',	action = 'version',		version = '%(prog)s 0.1' )
	gap.add_argument(		'--program',	action = 'store',		dest = "prog",		metavar = "prog",			default = os.path.basename(re.sub(".py", "", sys.argv[0])))
	gap = ap.add_argument_group( 'standard functionality' )
	gap.add_argument(		'--dryrun',		action = 'store_true' )
	gap.add_argument(		'--force',		action = 'store_true' )
	gap.add_argument( '-v',	'--verbose',	action = 'count',		default = 1 )
	gap.add_argument( '-f',	'--file',		action = 'store',		dest = "file",		metavar = "file" )
	gap = ap.add_argument_group( 'logging' )
	gap.add_argument( 		'--loglevel',	action = 'store',		dest = "loglevel",	metavar = "logging level",	default = 'info',	choices = ['crit', 'error', 'warn', 'notice', 'info', 'verbose', 'debug', 'insane'] )
	gap.add_argument(		'--logfile',	action = 'store',		dest = "logfile",	metavar = "logfile" )
	gap = ap.add_argument_group( 'output options' )
	gap.add_argument(		'--pprint',		action = 'store_true' )
	gap.add_argument(		'--save',		action = 'store_true' )
	gap.add_argument( '-o',	'--outfile',	action = 'store',		dest = "outfile",	metavar = "outfile",		default = ( '%s.html' % (os.path.basename(re.sub(".py", "", sys.argv[0])))) )
	
	ProgArgs								= ap.parse_args()
	Logger									= initLog( ProgArgs.loglevel, ProgArgs.logfile )
	
	return ProgArgs
###------------------------------------------------------------------------------------------------------------------------------
def initLog( LLevel, LogFile = None, module = None ):
	initLogger										= logging.getLogger( __name__ )
	LogLevels = {'crit':logging.CRITICAL,
				'error':logging.ERROR,
				'warn':logging.WARNING,
				'info':logging.INFO,
				'debug':logging.DEBUG }
	LogLevel										= LogLevels.get( LLevel, logging.NOTSET )
	initLogger.setLevel( LogLevel )
	LogFormat										= '(%(asctime)-11s)  :%(levelname)-9s:%(funcName)-13s:%(message)s'
	if ( len( initLogger.handlers ) == 0 ):
		try:
			Colorize								= __import__( 'logutils.colorize', fromlist=['colorize'] )
			LogHandler								= Colorize.ColorizingStreamHandler()
			LogHandler.level_map[logging.DEBUG]		= (None, 'blue', False)
			LogHandler.level_map[logging.INFO]		= (None, 'green', False)
			LogHandler.level_map[logging.WARNING]	= (None, 'yellow', False)
			LogHandler.level_map[logging.ERROR]		= (None, 'red', False)
			LogHandler.level_map[logging.CRITICAL]	= ('red', 'white', False)
		except ImportError:
			LogHandler	= logging.StreamHandler()
	else:
		LogHandler	= logging.StreamHandler()
	LogHandler.setFormatter( logging.Formatter( LogFormat, datefmt='%I:%M:%S %p' ) )
	initLogger.addHandler( LogHandler )
	if LogFile:
		LogFHandler									= logging.FileHandler( LogFile )
		LogFHandler.setLevel( 'DEBUG' )
		LogFHandler.setFormatter( logging.Formatter( LogFormat, datefmt='%I:%M:%S %p' ) )
		initLogger.addHandler( LogFHandler )
	return initLogger
###------------------------------------------------------------------------------------------------------------------------------
def LibImport( libPath, libFile ):
	if ( not os.path.isdir( libPath ) ):
		pStatus( 3 )
	else:
		if ( not os.path.isfile( libFile ) ):
			pStatus( 4 )
		else:
			sys.path.append( os.path.abspath( libPath ) )
			actLib									= re.sub( ".py$", "", libFile )
			actLib									= re.sub( "^.*/", "", actLib )
			#exec( "import %s as LibImport" % actLib )
			LibImport								= __import__( actLib )
	return LibImport
###------------------------------------------------------------------------------------------------------------------------------
def pStatus( status ):
	if ( status > 0 ):
		if ( status == 1 ):
			Logger.error("Error: Problem parsing arguments.")
		elif ( status == 2 ):
			Logger.error("Error: File not found.")
		elif ( status == 3 ):
			Logger.error("Error: MediaInfo Python library path not found.")
		elif ( status == 4 ):
			Logger.error("Error: MediaInfo Python library not found.")
		sys.exit( status )
	return True
###------------------------------------------------------------------------------------------------------------------------------
def main():
	ProgArgs										= argparser()
	if ( not ProgArgs ):
		pStatus( 1 )
	if ( not os.path.isfile( ProgArgs.file ) ):
		pStatus( 2 )
		
	###--- Import MediaInfoDLL ------------------------------------------------------------------------
	PyMediaInfoPath									= "/usr/include/MediaInfoDLL"
	PyMediaInfoLibFile								= "/usr/include/MediaInfoDLL/MediaInfoDLL.py"
	PyMedia											= LibImport( PyMediaInfoPath, PyMediaInfoLibFile )
	###------------------------------------------------------------------------------------------------
		
	return pStatus( 0 )
###------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	main()
###------------------------------------------------------------------------------------------------------------------------------