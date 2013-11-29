#!/bin/python

import	logging
import	os
import	re
import	sys
from	bs4				import NavigableString, BeautifulSoup	as bSoup
from 	datahandler		import DataHandler
from	handbrake		import HandBrake
from 	mediainfo		import MediaInfo	as MediaInfo
from 	mediainfo		import Track		as TrackInfo

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
	gap.add_argument( '-d',	'--directory',	action = 'store',		dest = "directory",	metavar = "directory" )
	gap.add_argument( '-f',	'--file',		action = 'store',		dest = "file",		metavar = "file" )
	gap.add_argument( '-i',	'--info',		action = 'store_true' )
	gap.add_argument( '-v',	'--verbose',	action = 'count',		default = 1 )
	gap.add_argument( 		'--isopath',	action = 'store',		dest = "isopath",	metavar = "ISO Mount Path",	default = "isotmp" )
	gap = ap.add_argument_group( 'logging' )
	gap.add_argument( 		'--loglevel',	action = 'store',		dest = "loglevel",	metavar = "logging level",	default = 'info',	choices = ['crit', 'error', 'warn', 'notice', 'info', 'verbose', 'debug', 'insane'] )
	gap.add_argument(		'--logfile',	action = 'store',		dest = "logfile",	metavar = "logfile" )
	gap = ap.add_argument_group( 'output options' )
	gap.add_argument(		'--pprint',		action = 'store_true' )
	gap.add_argument(		'--save',		action = 'store_true' )
	gap.add_argument( 		'--format',		action = 'store',		dest = "format",	metavar = "format",			default = "normal",	choices = ['html', 'normal', 'xml'] )
	gap.add_argument( '-o',	'--outfile',	action = 'store',		dest = "outfile",	metavar = "outfile",		default = ( '%s' % (os.path.basename(re.sub("\.py$", "", sys.argv[0])))) )
	gap.add_argument(		'--audio',		action = 'store_true' )
	gap.add_argument(		'--chapters',	action = 'store_true' )
	gap.add_argument(		'--video',		action = 'store_true' )
	gap.add_argument(		'--subtitles',	action = 'store_true' )
	gap.add_argument(		'--language',	action = 'store',		dest = "lang",		metavar = "lang",			default = "english",	choices = ['english', 'spanish', 'french', 'german'] )
	gap = ap.add_argument_group( 'handbrake options' )
	gap.add_argument(	'--handbrake',	action = 'store_true' )
	gap.add_argument(	'--hbtitle',	action = 'store',	dest = "hbtitle",	metavar = "DVD Title",			default = "1" )
	gap.add_argument(	'--hbdir',		action = 'store',	dest = "hbdir",		metavar = "Output Directory",	default = "encode" )
	gap.add_argument(	'--hbangle',	action = 'store',	dest = "hbangle",	metavar = "DVD Angle",			default = "1" )
	gap.add_argument(	'--hbverbose',	action = 'store',	dest = "hbverbose",	metavar = "Handbrake Verosity",	default = "2",		choices = ['0','1','2'] )
	gap.add_argument(	'--hbpreset',	action = 'store',	dest = "hbpreset",	metavar = "x264 Preset",		default = "slow",	choices = ['ultrafast','superfast','veryfast','faster','fast','medium','slow','slower','veryslow','placebo'] )
	gap.add_argument(	'--hbprofile',	action = 'store',	dest = "hbprofile",	metavar = "x264 Profile",		default = "high",	choices = ['auto','high','main','baseline'] )
	gap.add_argument(	'--hblevel',	action = 'store',	dest = "hblevel",	metavar = "x264 Profile Level",	default = "4.1",	choices = ['4.0','4.1','4.2','5.0','5.1','5.2'] )
	gap.add_argument(	'--hbformat',	action = 'store',	dest = "hbformat",	metavar = "Output Format",		default = "mkv",	choices = ['mkv','mp4'] )
	gap.add_argument(	'--hbfrc',		action = 'store',	dest = "hbfrc",		metavar = "Frame Rate Control",	default = "vfr",	choices = ['vfr','cfr','pfr'] )
	gap.add_argument(	'--hbcvq',		action = 'store',	dest = "hbcvq",		metavar = "Constant Quality",	default = "23",		choices = ['18','19','20','21','22','23','24','25'] )
	gap.add_argument(	'--hblang',		action = 'store',	dest = "hblang",	metavar = "Language",			default = "English",choices = ['English','Spanish','French','Russian','Chinese','Japanese'] )
	gap.add_argument(	'--hbmodulus',	action = 'store',	dest = "hbmodulus",	metavar = "Modulus",			default = "16",		choices = ['16','8','4'] )
	gap.add_argument(	'--hbencoder',	action = 'store',	dest = "hbencoder",	metavar = "Encoding Library",	default = "x264",	choices = ['x264','ffmpeg4','ffmpeg2','theora'] )
	gap.add_argument(	'--hbnatlang',	action = 'store',	dest = "hbnatlang",	metavar = "Native Language",	default = "eng",	choices = ['eng','fra','spa','rus'] )
	gap.add_argument(	'--hbcmarker',	action = 'store',	dest = "hbcmarker",	metavar = "Chapter Markers",	default = "notset" )
	
	ProgArgs								= ap.parse_args()
	
	Logger									= initLog( ProgArgs.loglevel, ProgArgs.logfile )
	if ( not ProgArgs.file ) and ( not ProgArgs.directory ):
		Logger.error( "Must use -d or -f option.")
		sys.exit(1)
	elif ( ProgArgs.file ) and ( ProgArgs.directory ):
		Logger.error( "Must use either -d or -f option, not both.")
		sys.exit(1)
	elif ( ProgArgs.file != None ):
		if ProgArgs.hbcmarker == "notset":
			ProgArgs.hbcmarker						= ( '/tmp/%s' % ( os.path.basename(re.sub('\.mkv$', ".csv", ProgArgs.file ) ) ) )
	
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
def fileType( fileName ):
		index										= fileName.split('.')
		idxLength									= len( index )
		fileType									= index[idxLength-1]
		return fileType
###------------------------------------------------------------------------------------------------------------------------------
def GetChapters( xmlData ):
	Chapter										= {}
	xmlInform									= bSoup( xmlData, "xml" )
	ChapCount									= 0
	for ChapterData in xmlInform.find_all( "track", type="Menu" ):
		for child in ChapterData.children:
			if ( len( child.string.strip() ) > 0 ):
				ChapCount						+= 1
				Chapter[ChapCount]				= child.string.strip()
	return Chapter
###------------------------------------------------------------------------------------------------------------------------------
def GetInform( MInfo, DataFormat ):
	InformData									= MInfo.InformData( DataFormat )
	return InformData
###------------------------------------------------------------------------------------------------------------------------------
def GetTracks( TrackSoup, Type, MediaType = "file" ):
	TInfo										= TrackInfo( TrackSoup, Type, MediaType, Logger )
	Track										= TInfo.TrackInfo()
	return Track
###------------------------------------------------------------------------------------------------------------------------------
def isNum( value ):
    try:
        float( value )
        return True
    except ValueError:
        return False
###------------------------------------------------------------------------------------------------------------------------------
def PrintTrack( Track ):
	Type										= Track["type"]
	TrackID										= Track["trackid"]
	Language									= Track["language"]
	Default										= Track["default"]
	try:
		Forced									= Track["forced"]
	except:
		Forced									= None
	if Type == "video":
		FormatProfile							= Track["formatprofile"]
		print( "\t   Type: %s\t\tTrackID: %s\t\t\tFormat Profile: %s\tLanguage: %s\tDefault: %s\tForced: %s" % ( Type, TrackID, FormatProfile, Language, Default, Forced ) )
	elif Type == "audio":
		try:
			StreamID							= Track["streamid"]
		except:
			StreamID							= None
		Format									= Track["format"]
		Channels								= Track["channels"]
		print( "\t   Type: %s\t\tTrackID: %s\tStreamID: %s\tFormat: %s\tChannels: %s\tLanguage: %s\tDefault: %s\tForced: %s" % ( Type, TrackID, StreamID, Format, Channels, Language, Default, Forced ) )
	elif Type == "subtitle":
		try:
			StreamID							= Track["streamid"]
		except:
			StreamID							= None
		if ( Language == "English" ):
			print( "\t   Type: %s\tTrackID: %s\tStreamID: %s\t\t\t\t\tLanguage: %s\tDefault: %s\tForced: %s" % ( Type, TrackID, StreamID, Language, Default, Forced ) )
###------------------------------------------------------------------------------------------------------------------------------
def PrintXMLData( xmlData ):
	xmlInform									= bSoup( xmlData, "xml" )
	InformData									= xmlInform.prettify()
	print(InformData)
###------------------------------------------------------------------------------------------------------------------------------
def PrintTrackData( xmlData, MediaType = "file" ):
	xmlInform									= bSoup( xmlData, "xml" )
	Keys										= ['subtitle', 'audio', 'video']
	Values										= ['Text', 'Audio', 'Video']
	TrackTypeDict								= dict( zip( Keys, Values ) )
	for Type, SearchKey in TrackTypeDict.iteritems():
		if ( Type == "video" ):
			print( "\t===== Video Tracks ===========================================================================================================" )
			for TrackSoup in xmlInform.find_all( "track", type=SearchKey ):
				Track							= GetTracks( TrackSoup, Type, MediaType )
				PrintTrack( Track )
		elif ( Type == "audio" ):
			print( "\t===== Audio Tracks ===========================================================================================================" )
			for TrackSoup in xmlInform.find_all( "track", type=SearchKey ):
				Track							= GetTracks( TrackSoup, Type, MediaType )
				PrintTrack( Track )
		elif ( Type == "subtitle" ):
			print( "\t===== Subtitle Tracks ========================================================================================================" )
			for TrackSoup in xmlInform.find_all( "track", type=SearchKey ):
				Track							= GetTracks( TrackSoup, Type, MediaType )
				PrintTrack( Track )
	print( "\t===== Chapters ===============================================================================================================" )
	Chapters									= GetChapters( xmlData )
	for ChapterID, Chapter in Chapters.iteritems():
		print( "\t   Chapter %s:\t%s" % ( ChapterID, Chapter ) )
###------------------------------------------------------------------------------------------------------------------------------
def PrettyPrint( xmlData ):
	xmlInform									= bSoup( xmlData, "xml" )
	print( xmlInform.prettify() )
###------------------------------------------------------------------------------------------------------------------------------
def WriteChapterFile( ChapterList ):
	for Chapter in ChapterList:
		ChapterNum								= Chapter[0]
		ChapterText								= Chapter[1]
		ChapterText								= re.sub( "en:%s" % ( ChapterNum ), "en:Chapter %s" % ( ChapterNum ), ChapterText )
		#print( "Chapter: %s\tDescription: %s" % ( ChapterNum, ChapterText ) )
		OutFile									= ProgArgs.hbcmarker
		OutHandle								= DataHandler( OutFile )
		OutHandle.Write( "%s,%s" % ( ChapterNum, ChapterText ) )
	return True
###------------------------------------------------------------------------------------------------------------------------------
def GetTrackData( xmlData, MediaType = None ):
	Tracks										= []
	xmlInform									= bSoup( xmlData, "xml" )
	Keys										= ['subtitle', 'audio', 'video']
	Values										= ['Text', 'Audio', 'Video']
	TrackTypeDict								= dict( zip( Keys, Values ) )
	for Type, SearchKey in TrackTypeDict.iteritems():
		for TrackSoup in xmlInform.find_all( "track", type=SearchKey ):
			Tracks.append( GetTracks( TrackSoup, Type ) )
	Chapters									= GetChapters( xmlData )
	for ChapterID, ChapterText in Chapters.iteritems():
		Keys									= ['type', 'chapterid', 'chaptertext']
		Values									= ['chapter', ChapterID, ChapterText]
		ChapterDict								= dict( zip( Keys, Values ) )
		Tracks.append( ChapterDict )
	HandBrakeCLI								= HandBrake( ProgArgs, Tracks, MediaType = MediaType, Logger = Logger )
	if ( HandBrakeCLI.ChapterList != False ):
		if ( not ProgArgs.dryrun ):
			WriteChapterFile( HandBrakeCLI.ChapterList )
###------------------------------------------------------------------------------------------------------------------------------
def checkDir( Directory ):
	if not os.path.isdir( Directory ):
		if not ProgArgs.dryrun:
			os.mkdir( Directory )
		else:
			print( "Creating directory:\t\t\"%s\"" % Directory )
	if os.path.isdir( Directory ):
		return True
	else:
		return False
###------------------------------------------------------------------------------------------------------------------------------
def listDir( directory ):
	fList											= os.listdir( directory )
	for item in fList:
		if os.path.isdir( os.path.join( directory, item ) ):
			Logger.debug( "Directory: %s" % ( item ) )
		else:
			Logger.debug( "File: %s" % ( item ) )
###------------------------------------------------------------------------------------------------------------------------------
def isoMount( action, file = None ):
	import subprocess
	isoDir											= os.path.join( os.getcwd(), ProgArgs.isopath )
	if checkDir( isoDir ):
		if action == "mount":
			Command									= "sudo mount -o loop,ro \"%s\" \"%s\"" % ( file, isoDir )
		elif action == "unmount":
			Command									= "sudo umount \"%s\"" % ( isoDir )
		Pipe										= subprocess.Popen( Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True )
		StdOut, StdErr								= Pipe.communicate()
		StdOut, StdErr								= StdOut.strip(), StdErr.strip()
		ReturnCode									= Pipe.returncode
		if ReturnCode != 0:
			Logger.error( "%s" % ( StdErr ) )
			Status									= False
		else:
			Status									= True
		if ( action == "unmount" ) and ( Status == True ):
			os.rmdir( isoDir )
		#Logger.debug( "%s" % ( StdOut ) )
		#Logger.debug( "Return Code:\t%s" % ( Status ) )
	else:
		Logger.error( "Could not create directory:\t\"%s\"" % ( isoDir ) )
		Status										= False
	return Status
###------------------------------------------------------------------------------------------------------------------------------
def MediaPath( directory ):
	fList											= os.listdir( directory )
	for item in fList:
		if ( item == "BDMV" ) or ( item == "VIDEO_TS" ):
			if os.path.isdir( os.path.join( directory, item ) ):
				if ( item == "BDMV" ):
					MediaPath						= os.path.join( directory, item )
					MediaPath						= os.path.join( MediaPath, "STREAM" )
				elif ( item == "VIDEO_TS" ):
					MediaPath						= os.path.join( directory, item )
			else:
				MediaPath							= None
	return MediaPath
###------------------------------------------------------------------------------------------------------------------------------
def main():
	global	ProgArgs
	isoMounted										= False
	ProgArgs										= argparser()
	if ( not ProgArgs ):
		pStatus( 1 )
	if ProgArgs.file:
		if ( not os.path.isfile( ProgArgs.file ) ):
			pStatus( 2 )
	elif ProgArgs.directory:
		if ( not os.path.isdir( ProgArgs.directory ) ):
			pStatus( 3 )
		
	if ( ProgArgs.info ):
		success										= Info( ProgArgs )
		
	if ProgArgs.file != None:
		if ( fileType( ProgArgs.file ) == 'mkv' ) or ( fileType( ProgArgs.file ) == 'mp4' ):
			mType									= "video"
			MInfo									= MediaInfo( ProgArgs.file, Type = mType, Logger = Logger )
		elif fileType( ProgArgs.file ) == 'iso':
			isoDir									= os.path.join( os.getcwd(), ProgArgs.isopath )
			if ( isoMount( "mount", ProgArgs.file ) ):
				isoMounted							= True
				Logger.info( "Mounted ISO File: \"%s\"\tto: \"%s\"" % ( ProgArgs.file, isoDir ) )
				listDir( isoDir )
			if MediaPath( isoDir ) != None:
				mType								= "directory"
				MInfo								= MediaInfo( MediaPath( isoDir ), Type = mType, Logger = Logger )
			else:
				Logger.error( "No media content found.")
	elif ProgArgs.directory != None:
		mType										= "directory"
		MInfo										= MediaInfo( ProgArgs.directory, Type = mType, Logger = Logger )
	else:
		sys.exit(2)
	
	DataFormat										= "xml"
	xmlData											= GetInform( MInfo, DataFormat )
	
	if ( ProgArgs.pprint ):
		PrintXMLData( xmlData )
		PrintTrackData( xmlData, MediaType = mType )
	
	if ( ProgArgs.dryrun ):
		PrettyPrint( xmlData )
		
	if ( ProgArgs.handbrake ):
		GetTrackData( xmlData, MediaType = mType )
	if isoMounted:
		if ( isoMount( "unmount" ) ):
			Logger.info( "Unounted ISO File: \"%s\"\tfrom: \"%s\"" % ( ProgArgs.file, os.path.join( os.getcwd(), ProgArgs.isopath ) ) )

	return pStatus( 0 )
###------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	main()
###------------------------------------------------------------------------------------------------------------------------------
