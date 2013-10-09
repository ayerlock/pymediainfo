import	os
import	re
import	sys
from	tempfile			import mkstemp
from	xml.parsers.expat	import ExpatError
try:
    import	simplejson		as json
except ImportError:
    import	json
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
			#exec( "import %s as LibImport" % actLib )
			LibImport								= __import__( actLib )
	return LibImport
###------------------------------------------------------------------------------------------------------------------------------
class MediaInfo( object ):
	def __init__( self, MediaFile, Logger ):
		self.MediaFile								= MediaFile
		self.Logger									= Logger
		self.InfoType								= "normal"
		self.MIPath									= "/usr/include/MediaInfoDLL"
		self.MILib									= "/usr/include/MediaInfoDLL/MediaInfoDLL.py"
		self.MediaInfoDLL							= LibImport( self.MIPath, self.MILib )
		self.MInfo									= self.MediaInfoDLL.MediaInfo()
		if ( os.path.isfile( self.MediaFile ) ):
			self.Logger.debug( "Found Media File:%s" % ( self.MediaFile ) )
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
		if ( self.MInfo.Open( self.MediaFile ) ):
			self.Logger.debug( "Opened Media File:\t%s" % ( self.MediaFile ) )
		else:
			self.Logger.error( "Error Opening Media File:\t%s" % ( self.MediaFile ) )
		return True
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
	def __init__( self, TrackSoup, TrackType ):
		self.TrackSoup								= TrackSoup
		self.TrackType								= TrackType
		self.TrackDict								= {}
		if ( self.TrackType == "audio" ):
			self.Keys								= ['index', 'audio', 'streamid', 'ID', 'Format', 'Channel_s_', 'Language', 'Title', 'Default', 'Forced']
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
			else:
				Data								= self.TrackSoup.find_next( Key ).get_text().strip()
				self.TrackDict[Value]				= re.sub( " .*$", "", Data )
		return self.TrackDict
###------------------------------------------------------------------------------------------------------------------------------
class MediaInfoDLL( object ):
	def __init__( self, MediaFile, Logger ):
		self.MediaFile								= MediaFile
		self.Logger									= Logger
		self.InfoType								= "normal"
		self.MIPath									= "/usr/include/MediaInfoDLL"
		self.MILib									= "/usr/include/MediaInfoDLL/MediaInfoDLL.py"
		self.MediaInfoDLL							= LibImport( self.MIPath, self.MILib )
		self.MInfo									= self.MediaInfoDLL
		if ( os.path.isfile( self.MediaFile ) ):
			self.Logger.debug( "Found Media File:%s" % ( self.MediaFile ) )
	###------------------------------------------------------------------------------------------------
	def DLLInfo( self ):
		from pprint import pprint
		#help(self.MInfo)
		self.myList									= dir( self.MInfo )
		self.myDict									= self.MInfo.__dict__
		pprint( self.myList )
		pprint( self.myDict, indent=2 )
###------------------------------------------------------------------------------------------------------------------------------
'''
class Track(object):
	def __getattribute__( self, Name ):
		try:
			return object.__getattribute__( self, Name )
		except:
			pass
		return None
	###------------------------------------------------------------------------------------------------
	def __init__( self, xmlDomFragment ):
		self.xmlDomFragment						= xmlDomFragment
		self.trackType							= xmlDomFragment.attrs['type']
		
		for el in self.xmlDomFragment.children:
			if not isinstance( el, NavigableString ):
				nodeName						= el.name.lower().strip().strip('_')
				if nodeName == 'id':
					nodeName					= 'track_id'
				nodeValue						= el.string
				otherNodeName					= ( "other_%s" % ( nodeName ) )
				if getattr( self, nodeName ) is None:
					setattr( self, nodeName, nodeValue )
				else:
					if getattr( self, otherNodeName ) is None:
						setattr( self, otherNodeName, [nodeValue, ])
					else:
						getattr( self, otherNodeName ).append( nodeValue )

		for o in [d for d in self.__dict__.keys() if d.startswith('other_')]:
			try:
				primary							= o.replace('other_', '')
				setattr( self, primary, int( getattr( self, primary ) ) )
			except:
				for v in getattr(self, o):
					try:
						current					= getattr( self, primary )
						setattr( self, primary, int( v ) )
						getattr( self, o ).append( current )
						break
					except:
						pass
	###------------------------------------------------------------------------------------------------
	def __repr__(self):
		return( "<Track track_id='{0}', track_type='{1}'>".format( self.track_id, self.track_type ) )
	###------------------------------------------------------------------------------------------------
	def to_data(self):
		data									= {}
		for k, v in self.__dict__.iteritems():
			if k != 'xml_dom_fragment':
				data[k]							= v
		return data
###------------------------------------------------------------------------------------------------------------------------------
class MediaInfoXML( object ):
	def __init__( self, xmlData ):
		self.xmlData								= xmlData
		self.xmlDom									= self.xmlData
        if _python3: self.xmlTypes					= (str,)				# No unicode type in python3
        else: self.xmlTypes							= (str, unicode)
        if isinstance( self.xmlData, self.xmlTypes ):
            self.xmlDom								= MediaInfoXML.parse_xml_data_into_dom( self.xmlData )
	###------------------------------------------------------------------------------------------------
	@staticmethod
	def parse_xml_data_into_dom( xmlData ):
		return bSoup( xmlData, "xml" )
	###------------------------------------------------------------------------------------------------
	@staticmethod
	def parse( xmlData ):
		xmlDom										= MediaInfoXML.parse_xml_data_into_dom( xmlData )
		return MediaInfo( xmlDom )
	###------------------------------------------------------------------------------------------------
	def _populate_tracks( self ):
		if self.xmlDom is None:
			return
		for xmlTrack in self.xmlDom.Mediainfo.File.find_all( "track" ):
			self._tracks.append( Track( xmlTrack ) )
	###------------------------------------------------------------------------------------------------
	@property
	def tracks( self ):
		if not hasattr( self, "_tracks" ):
			self._tracks = []
		if len(self._tracks) == 0:
			self._populate_tracks()
		return self._tracks
	###------------------------------------------------------------------------------------------------
	def to_data( self ):
		data = {'tracks': []}
		for track in self.tracks:
			data['tracks'].append( track.to_data() )
		return data
	###------------------------------------------------------------------------------------------------
	def to_json( self ):
		return json.dumps( self.to_data() )
###------------------------------------------------------------------------------------------------------------------------------
'''
