#!/bin/python

import	logging
import	os
import	re
import	sys
from	bs4				import NavigableString, BeautifulSoup	as bSoup
from 	datahandler		import DataHandler
from 	pymediainfo		import MediaInfo	as MediaInfo
from 	pymediainfo		import MediaInfoDLL	as MediaInfoDLL

sys.setrecursionlimit(5000)
###------------------------------------------------------------------------------------------------------------------------------
def argparser():
	import argparse
	
	global Logger
	ap = argparse.ArgumentParser( description = 'A pythonized front end to MediaInfo.', prog = os.path.basename(re.sub("\.py$", "", sys.argv[0])) )
	gap = ap.add_argument_group( 'program information' )
	gap.add_argument( 		'--version',	action = 'version',		version = '%(prog)s 0.1' )
	gap.add_argument(		'--program',	action = 'store',		dest = "prog",		metavar = "prog",			default = os.path.basename(re.sub("\.py#", "", sys.argv[0])))
	gap = ap.add_argument_group( 'standard functionality' )
	gap.add_argument(		'--dryrun',		action = 'store_true' )
	gap.add_argument(		'--force',		action = 'store_true' )
	gap.add_argument( '-f',	'--file',		action = 'store',		dest = "file",		metavar = "file" )
	gap.add_argument( '-i',	'--info',		action = 'store_true' )
	gap.add_argument( '-v',	'--verbose',	action = 'count',		default = 1 )
	gap = ap.add_argument_group( 'logging' )
	gap.add_argument( 		'--loglevel',	action = 'store',		dest = "loglevel",	metavar = "logging level",	default = 'info',	choices = ['crit', 'error', 'warn', 'notice', 'info', 'verbose', 'debug', 'insane'] )
	gap.add_argument(		'--logfile',	action = 'store',		dest = "logfile",	metavar = "logfile" )
	gap = ap.add_argument_group( 'output options' )
	gap.add_argument(		'--pprint',		action = 'store_true' )
	gap.add_argument(		'--save',		action = 'store_true' )
	gap.add_argument( 		'--format',		action = 'store',		dest = "format",	metavar = "format",			default = "normal",	choices = ['html', 'normal', 'xml'] )
	gap.add_argument( '-o',	'--outfile',	action = 'store',		dest = "outfile",	metavar = "outfile",		default = ( '%s' % (os.path.basename(re.sub("\.py$", "", sys.argv[0])))) )
	
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
def SaveInfo( InformData ):
	MInfo										= MediaInfo( ProgArgs.file, Logger )
	if ( ProgArgs.pprint ):
		Logger.debug( "Output Format:\t%s" % ( ProgArgs.format ) )
		if ( ProgArgs.format == "html" ):
			InformSoup							= bSoup( MInfo.InformData( ProgArgs.format ), "html5lib" )
			InformData							= InformSoup.prettify()
		elif ( ProgArgs.format == "xml" ):
			InformSoup							= bSoup( MInfo.InformData( ProgArgs.format ), "xml" )
			InformData							= InformSoup.prettify()
		else:
			InformData							= InformData( MInfo.ProgArgs.format )
	
	if ( ProgArgs.outfile ):
		CurrentDir								= os.getcwd()
		OutFile									= ( "%s/%s.%s" % ( CurrentDir, ProgArgs.outfile, MInfo.InfoType ) )
		OutHandle								= DataHandler( OutFile )
		if ( InformData ):
			OutHandle.Write( InformData )
		else:
			Logger.error( "Error getting media information from file.")
	else:
		if ( InformData ):
			print( InformData )
		else:
			Logger.error( "Error getting media information from file.")
	return True
###------------------------------------------------------------------------------------------------------------------------------
def DLLInfo():
	MInfo										= MediaInfo( ProgArgs.file, Logger )
	MInfo.DLLInfo()
###------------------------------------------------------------------------------------------------------------------------------
def GetInform():
	MInfo										= MediaInfo( ProgArgs.file, Logger )
	InformData									= MInfo.InformData( ProgArgs.format )
	return InformData
###------------------------------------------------------------------------------------------------------------------------------
def main():
	global	ProgArgs
	ProgArgs									= argparser()
	if ( not ProgArgs ):
		pStatus( 1 )
	if ( not os.path.isfile( ProgArgs.file ) ):
		pStatus( 2 )
		
	if ( ProgArgs.info ):
		success									= Info( ProgArgs )
		
	MInfo										= MediaInfo( ProgArgs.file, Logger )
	
	#print( MInfo.Get( "menu", "first", "Chapters_Pos_Begin", "", ProgArgs.format ) )
	#InformData									= GetInform( ProgArgs ) )
	#DLLInfo( ProgArgs )
	xmlInform									= bSoup( GetInform(), "xml" )
	print( xmlInform.Prettify() )
	
	return pStatus( 0 )
###------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	main()
###------------------------------------------------------------------------------------------------------------------------------