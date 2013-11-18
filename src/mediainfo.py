import	os
import	re
import	subprocess
import	sys
###------------------------------------------------------------------------------------------------------------------------------
_python3											= sys.version_info >= (3,)
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
			LibImport								= __import__( actLib )
	return LibImport
###------------------------------------------------------------------------------------------------------------------------------
class MediaInfo( object ):
	def __init__( self, SourceMedia, Logger ):
		self.SourceMedia							= SourceMedia
		self.Logger									= Logger
		self.InfoType								= "normal"
		self.MIPath									= "/usr/include/MediaInfoDLL"
		self.MILib									= "/usr/include/MediaInfoDLL/MediaInfoDLL.py"
		self.MediaInfoDLL							= LibImport( self.MIPath, self.MILib )
		self.MInfo									= self.MediaInfoDLL.MediaInfo()
		if ( os.path.isfile( self.SourceMedia ) ):
			self.fType( self.SourceMedia )
			self.Logger.debug( "Found Media File:%s" % ( self.SourceMedia ) )
		elif ( os.path.isdir( self.SourceMedia ) ):
			self.Logger.debug( "Found Media File:%s" % ( self.SourceMedia ) )
	###------------------------------------------------------------------------------------------------
	def fType( self, fName ):
		index										= fName.split('.')
		idxLength									= len( index )
		self.fExt									= index[idxLength-1]
		sys.exit()
	###------------------------------------------------------------------------------------------------
	def DLLInfo( self ):
		from pprint import pprint
		#help(self.MInfo)
		self.myList									= dir( self.MInfo )
		self.myDict									= self.MInfo.__dict__
		pprint( self.myList )
		pprint( self.myDict, indent=2 )
	###------------------------------------------------------------------------------------------------
	def OpenMFile( self ):
		if ( os.path.isfile( self.SourceMedia  ) ):
			if ( self.MInfo.Open( self.SourceMedia ) ):
				self.Logger.debug( "Opened Media File:\t%s" % ( self.SourceMedia ) )
				return True
			else:
				self.Logger.error( "Error Opening Media File:\t%s" % ( self.SourceMedia ) )
				return False
		elif ( os.path.isdir( self.SourceMedia  ) ):
			return False
	###------------------------------------------------------------------------------------------------
	def CloseMFile( self ):
		self.MInfo.Close()
		return True
	###------------------------------------------------------------------------------------------------
	def Get( self, SType, SNum, Param, Kind, InfoType = "normal" ):
		self.InfoType								= InfoType
		if ( self.OpenMFile() ):
			if ( self.InfoType == "html" ):
				self.MInfo.Option( "Inform", "HTML" )
			elif ( self.InfoType == "xml" ):
				self.MInfo.Option( "Inform", "XML" )
			self.Get								= self.MInfo.Get( SType, SNum, Param )
		return self.Get
	###------------------------------------------------------------------------------------------------
	def GetInfo( self ):
		if ( self.OpenMFile() ):
			if ( self.InfoType == "html" ):
				self.MInfo.Option( "Inform", "HTML" )
			elif ( self.InfoType == "xml" ):
				self.MInfo.Option( "Inform", "XML" )
			#MediaInfo.Option( "Complete", "1" )
			self.InformData							= self.MInfo.Inform()
			self.CloseMFile()
		else:
			if ( os.path.isdir( self.SourceMedia ) ):
				Command								= "mediainfo --Output=XML %s" % ( self.SourceMedia )
				SubData								= subprocess.Popen( Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True )
				InformData, StdErr					= SubData.communicate()
				self.InformData						= InformData.strip()
	###------------------------------------------------------------------------------------------------
	def InformData( self, InfoType = "normal" ):
		self.InfoType								= InfoType
		try:
			self.GetInfo()
		except:
			return False
		else:
			return self.InformData
	###------------------------------------------------------------------------------------------------
	def InfoType( self ):
		return self.InfoType
###------------------------------------------------------------------------------------------------------------------------------
class Track( object ):
	def __init__( self, TrackSoup, TrackType, MediaType, Logger ):
		self.Logger									= Logger
		self.MediaType								= MediaType
		self.TrackSoup								= TrackSoup
		self.TrackType								= TrackType
		self.TrackDict								= {}
		if ( self.TrackType == "audio" ):
			self.Keys								= ['index', 'audio', 'streamid', 'ID', 'Format', 'Channel_count', 'Language', 'Title', 'Default', 'Forced']
			self.Values								= ['0', 'type', 'streamid', 'trackid', 'format', 'channels', 'language', 'title', 'default', 'forced']
		elif ( self.TrackType == "subtitle" ):
			self.Keys								= ['index', 'subtitle', 'streamid', 'ID', 'Language', 'Default', 'Forced']
			self.Values								= ['0', 'type', 'streamid', 'trackid', 'language', 'default', 'forced']
		elif ( self.TrackType == "video" ):
			self.Keys								= ['index', 'video', 'streamid', 'ID', 'Format_profile', 'Language', 'Default', 'Forced']
			self.Values								= ['0', 'type', 'streamid', 'trackid', 'formatprofile', 'language', 'default', 'forced']
		self.Dict									= dict( zip( self.Keys, self.Values ) )
	###------------------------------------------------------------------------------------------------
	def TrackInfo( self ):
		# This performs an inverse mapping of Values to data found searching for Keys in the TrackSoup
		for Key, Value in self.Dict.iteritems():
			if ( Value == "type" ):
				self.TrackDict[Value]				= Key
			elif ( Key == "index" ):
				self.TrackDict[Key]					= "0"
			elif ( Value == "streamid" ):
				if self.TrackSoup.has_attr( Key ):
					self.TrackDict[Value]			= self.TrackSoup[Key].strip()
			elif ( Value == "language" ):
				try:
					self.TrackDict[Value]			= self.TrackSoup.find_next( Key ).get_text().strip()
				except:
					self.TrackDict[Value]				= u"Unknown"
			elif ( Value == "title" ):
				try:
					self.TrackDict[Value]			= self.TrackSoup.find_next( Key ).get_text().strip()
				except:
					self.TrackDict[Value]				= u"None"
			elif ( Value == "forced" ):
				try:
					self.TrackDict[Value]			= self.TrackSoup.find_next( Key ).get_text().strip()
				except:
					self.TrackDict[Value]				= u"None"
			elif ( Value == "default" ):
				try:
					self.TrackDict[Value]			= self.TrackSoup.find_next( Key ).get_text().strip()
				except:
					self.TrackDict[Value]				= u"None"
			else:
				try:
					Data								= self.TrackSoup.find_next( Key ).get_text().strip()
				except:
					self.Logger.error( "\tError trying to retrieve Key:\t%s" % ( Key ) )
				else:
					self.TrackDict[Value]				= re.sub( " .*$", "", Data )
		return self.TrackDict
###------------------------------------------------------------------------------------------------------------------------------
