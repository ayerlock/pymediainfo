import	os
import	re
import	sys
###------------------------------------------------------------------------------------------------------------------------------
class HandBrake( object ):
	def __init__( self, ProgArgs, Tracks, MediaType = None, Logger = None ):
		self.Logger										= Logger
		self.InFile										= ProgArgs.file
		self.OutFile									= "%s/%s" % ( ProgArgs.hbdir, re.sub( "MKV$", "mkv", self.InFile ) )
		self.Title										= ProgArgs.hbtitle
		self.Angle										= ProgArgs.hbangle
		self.Verbose									= ProgArgs.hbverbose
		self.Preset										= ProgArgs.hbpreset 
		self.Profile									= ProgArgs.hbprofile
		self.Level										= ProgArgs.hblevel
		self.Format										= ProgArgs.hbformat
		self.FrameControl								= ProgArgs.hbfrc
		self.ConstQual									= ProgArgs.hbcvq
		self.Language									= ProgArgs.hblang
		self.Modulus									= ProgArgs.hbmodulus
		self.Encoder									= ProgArgs.hbencoder
		self.NativeLang									= ProgArgs.hbnatlang
		self.ChapterFile								= ProgArgs.hbcmarker
		self.MediaType									= MediaType
		self.narrowTracks( Tracks )
		if ProgArgs.dryrun:
			self.DebugPrint()
		if self.MediaType == "iso":
			self.Logger.debug( "MediaType set to:\t%s" % ( self.MediaType ) )
			self.ImageCLI()
		elif self.MediaType == "video":
			self.Logger.debug( "MediaType set to:\t%s" % ( self.MediaType ) )
			self.ChapterList( Tracks )
			self.BuildCLI()
	###------------------------------------------------------------------------------------------------
	def narrowTracks( self, Tracks ):
		Narrowed										= False
		NarrowRules										= []
		# Narrow the list of desired video tracks.
		self.vTracks									= self.findTracks( Tracks, "video" )
		# Narrow the list of desired audio tracks.
		NarrowRules.append( 'language:English' )
		NarrowRules.append( 'format:DTS' )
		NarrowRules.append( 'channels:6' )
		NumRules										= len( NarrowRules )
		aTracks											= self.findTracks( Tracks, "audio" )
		if ( len( aTracks ) > 1 ):
			while ( len( aTracks ) > 1 ) and ( Narrowed == False ) and ( NumRules > 0 ):
				CurrentLength							= len( aTracks )
				Rule									= NarrowRules.pop(0)
				Key										= re.sub( ':.*$', '', Rule )
				Value									= unicode( re.sub( '^.*:', '', Rule ) )
				#print( "\t\tNarrowing based on\tKey: %s\tValue: %s" % ( Key, Value ) )
				if ( len ( self.selectTracks( aTracks, "audio", Key, Value, False ) ) >= 1 ):
					aTracks								= self.selectTracks( aTracks, "audio", Key, Value )
				NumRules								-= 1
		self.aTracks									= aTracks
		# Narrow the list of desired subtitle tracks.
		self.sTracks									= self.selectTracks( Tracks, "subtitle", "language", self.Language )
	###------------------------------------------------------------------------------------------------
	def DebugPrint( self ):
		print("\tAnalyzing Media: %s" % ( self.InFile ) )
		self.printTracks( self.vTracks, "video" )
		self.printTracks( self.aTracks, "audio" )
		self.printTracks( self.sTracks, "subtitle" )
	###------------------------------------------------------------------------------------------------
	def printTracks( self, Tracks, Type ):
		for Track in Tracks:
			print( "\t   Type: %s\tTrack: %s" % ( Type, Track ) )
	###------------------------------------------------------------------------------------------------
	def findTracks( self, Tracks, Type ):
		rTracks											= []
		rIndex											= 0
		for Track in Tracks:
			doAppend									= False
			for TKey, TValue in Track.iteritems():
				if ( TKey == "type" ) and ( TValue == Type ):
					doAppend							= True
			if ( doAppend ):
				Track['index']							= rIndex
				rIndex									+= 1
				rTracks.append( Track )
		return rTracks
	###------------------------------------------------------------------------------------------------
	def selectTracks( self, Tracks, Type, Key, Value, Print = True ):
		rTracks											= []
		rIndex											= 0
		for Track in self.findTracks( Tracks, Type ):
			doAppend									= False
			doPrint										= False
			if ( Track["type"] == Type ) and ( Type == "audio" ):
				if ( Track[Key] == Value ):
					doAppend							= True
					doPrint								= True
			elif ( Track["type"] == Type ) and ( Type == "subtitle" ):
				if ( Track[Key] == Value ):
					doAppend							= True
					doPrint								= False
			if ( doAppend ):
				Track['index']							= rIndex
				rIndex									+= 1
				rTracks.append(Track)
		return rTracks
	###------------------------------------------------------------------------------------------------
	def ChapterList( self, Tracks ):
		self.ChapterList								= []
		ChapterData										= self.findTracks( Tracks, "chapter" )
		self.ChapterCount								= len( ChapterData )
		if ( self.ChapterCount > 0 ):
			for Chapter in iter( ChapterData ):
				for Count in range( 1, self.ChapterCount ):
					if ( Count == Chapter["chapterid"] ):
						self.ChapterList.append([ Chapter["chapterid"], Chapter["chaptertext"] ] )
		if ( len( self.ChapterList ) == 0 ):
			self.ChapterList							= False
		return self.ChapterList
	###------------------------------------------------------------------------------------------------
	def AudioOptions( self, OptionList ):
		if ( len( self.aTracks ) == 1 ):
			for Track in self.aTracks:
				if Track['channels'] > 2:
					try:
						if Track['streamid'] != None:
							TrackIDs					= ( "%s,%s" % ( Track['streamid'], Track['streamid'] ) )
						else:
							TrackIDs					= "1,1"
						try:
							TrackLang					= Track['language']
							TrackTitle					= Track['title']
							if ( TrackLang == "English" ) and ( TrackTitle == "None" ):
								AudioNames				= ( '"%s", "%s (2ch. Pro Logic)"' % ( TrackLang, TrackLang ) )
							elif ( TrackLang != "English" ) and ( TrackTitle == "None" ):
								AudioNames				= ( '"%s", "%s (2ch. Pro Logic)"' % ( TrackLang, TrackLang ) )
							elif ( TrackLang == "English" ) and ( TrackTitle != "None" ):
								AudioNames				= ( '"%s", "%s (MixDown 2ch. Pro Logic)"' % ( TrackTitle, TrackTitle ) )
							else:
								AudioNames				= ( '"%s", "%s (MixDown 2ch. Pro Logic)"' % ( TrackTitle, TrackTitle ) )
						except:
							TrackLang					= Track['language']
							AudioNames					= ( '"%s", "%s (2ch. Pro Logic)"' % ( TrackLang, TrackLang ) )
					except:
						TrackLang						= Track['language']
						AudioNames						= ( '"%s", "%s (2ch. Pro Logic)"' % ( TrackLang, TrackLang ) )
				else:
					TrackIDs							= ( "1" )
					TrackLang							= Track['language']
					TrackTitle							= Track['title']
					AudioNames							= ( '"%s (2ch. Pro Logic)"' % ( TrackLang ) )
					if ( TrackLang == "English" ) and ( TrackTitle == "None" ):
						AudioNames						= ( '"%s"' % ( TrackLang ) )
					elif ( TrackLang != "English" ) and ( TrackTitle == "None" ):
						AudioNames						= ( '"%s"' % ( TrackLang ) )
					elif ( TrackLang == "English" ) and ( TrackTitle != "None" ):
						AudioNames						= ( '"%s"' % ( TrackTitle ) )
					else:
						AudioNames						= ( '"%s"' % ( TrackTitle ) )
			self.Logger.debug( "Track Language:\t%s" % TrackLang )
			self.Logger.debug( "Audio Names:\t%s" % AudioNames )
			TrackEncoders								= "copy,faac"
			self.Logger.debug( "Track Encoders:\t%s" % TrackEncoders )
			MixDowns									= "auto,dpl2" 
			self.Logger.debug( "Mix Downs:\t%s" % MixDowns )
			SampleRates									= "Auto,48"
			self.Logger.debug( "Sample Rates:\t%s" % SampleRates )
			AudioRates									= "0,160"
			self.Logger.debug( "Audio Rates:\t%s" % AudioRates )
		else:
			TrackIDs									= []
			TrackEncoders								= []
			MixDowns									= []
			SampleRates									= []
			AudioRates									= []
			AudioNames									= []
			for Track in self.aTracks:
				doAppend								= False
				try:
					TrackIDs.append( Track['streamid'] )
					doAppend							= True
				except:
					self.Logger.debug( "Skipping Audio Track:\t%s" % ( Track ) )
					#TrackIDs.append( None )
				if doAppend == True:
					TrackEncoders.append( "copy" )
					MixDowns.append( "auto" )
					SampleRates.append( "Auto" )
					AudioRates.append( "0" )
					TrackLang							= Track['language']
					TrackTitle							= Track['title']
					if ( TrackLang == "English" ) and ( TrackTitle == "None" ):
						AudioNames.append( '"English"' )
					elif ( TrackLang != "English" ) and ( TrackTitle == "None" ):
						AudioNames.append( '"%s"' % ( TrackLang ) )
					else:
						AudioNames.append( '"%s"' % ( TrackTitle ) )
			TrackIDs									= ','.join( str( TrackID ) for TrackID in TrackIDs )
			TrackEncoders								= ','.join( str( TrackEncoder ) for TrackEncoder in TrackEncoders )
			MixDowns									= ','.join( str( MixDown ) for MixDown in MixDowns )
			SampleRates									= ','.join( str( SampleRate ) for SampleRate in SampleRates )
			AudioRates									= ','.join( str( AudioRate ) for AudioRate in AudioRates )
			AudioNames									= ','.join( str( AudioName ) for AudioName in AudioNames )
			self.Logger.debug( "Track Language:\t%s" % TrackLang )
		try:
			OptionList.append( "--audio %s" % ( TrackIDs ) )
			self.Logger.debug( "Track IDs:\t%s" % TrackIDs )
		except:
			self.Logger.debug( "Unable to append option:\t--audio [trackid]")
		OptionList.append( "--aencoder %s" % ( TrackEncoders ) )
		self.Logger.debug( "Track Encoders:\t%s" % TrackEncoders )
		OptionList.append( "--mixdown %s" % ( MixDowns ) )
		self.Logger.debug( "Mix Downs:\t%s" % MixDowns )
		OptionList.append( "--arate %s" % ( SampleRates ) )
		self.Logger.debug( "Sample Rates:\t%s" % SampleRates )
		OptionList.append( "--ab %s" % ( AudioRates ) )
		self.Logger.debug( "Audio Rates:\t%s" % AudioRates )
		OptionList.append( "--drc 0,0" )
		OptionList.append( "--gain 0,0" )
		try:
			OptionList.append( "--aname %s" % ( AudioNames ) )
			self.Logger.debug( "Audio Names:\t%s" % AudioNames )
		except:
			self.Logger.debug( "Unable to append option:\t--aname [trackid]")
		OptionList.append( "--audio-fallback faac" )
		return( OptionList )
	###------------------------------------------------------------------------------------------------
	def SubtitleOptions( self, OptionList ):
		NumTracks										= len( self.sTracks )
		if ( NumTracks == 0 ):
			TrackIDs									= "scan"
		elif ( NumTracks == 1 ):
			try:
				TrackIDs								= ( "scan,%s" % ( Track['streamid'] ) )
			except:
				TrackIDs								= "scan,1"
		else:
			TrackIDs									= []
			TrackIDs.append( "scan" )
			for Track in self.sTracks:
				TrackIDs.append( Track['streamid'] )
			TrackIDs									= ','.join( str( TrackID ) for TrackID in TrackIDs )
		OptionList.append( "--subtitle %s" % ( TrackIDs ) )
		OptionList.append( "--native-language %s" % ( self.NativeLang ) )
		OptionList.append( "--native-dub" )
		return( OptionList )
	###------------------------------------------------------------------------------------------------
	def ImageCLI( self ):
		if "iso" in self.InFile:
			self.OutFile								= re.sub( "iso$", "mkv", self.InFile )
			self.Title									= "--main-feature"
			self.Format									= "libmkv"
			self.ChapterList							= False
		OptionList										= []
		OptionList.append( 'HandBrakeCLI' )
		OptionList.append( '--input "%s"' % ( self.InFile ) )
		OptionList.append( '--output "%s"' % ( self.OutFile ) )
		OptionList.append( '--format %s' % ( self.Format ) )
		OptionList.append( '--title %s' % ( self.Title ) )
		#OptionList.append( '--angle %s' % ( self.Angle ) )
		OptionList.append( '--verbose %s' % ( self.Verbose ) )
		OptionList.append( '--use-opencl' )
		OptionList.append( '--use-hwd' )
		OptionList.append( '--optimize' )
		OptionList.append( '--strict-anamorphic' )
		OptionList.append( '--decomb' )
		OptionList.append( '--modulus %s' % ( self.Modulus ) )
		OptionList.append( '--encoder %s' % ( self.Encoder ) )
		OptionList.append( '--x264-preset %s' % ( self.Preset ) )
		OptionList.append( '--h264-profile %s' % ( self.Profile ) )
		OptionList.append( '--h264-level %s' % ( self.Level ) )
		OptionList.append( '--quality %s' % ( self.ConstQual ) )
		OptionList.append( '--%s' % ( self.FrameControl ) )
		OptionList										= self.AudioOptions( OptionList )
		OptionList										= self.SubtitleOptions( OptionList )
		if ( self.ChapterFile != "notset" ):
			if ( not self.ChapterList == False ):
				try:
					OptionList.append( '--chapters 1-%s' % ( self.ChapterCount ) )
				except:
					pass
				OptionList.append( '--markers "%s"' % ( self.ChapterFile ) )
		self.Command									= ' '.join( str( Option ) for Option in OptionList )
		print( self.Command )
	###------------------------------------------------------------------------------------------------
	def BuildCLI( self ):
		self.OutFile									= re.sub( "\.ts$", ".mkv", self.OutFile )
		#self.OutFile									= re.sub( "\.mp4#", ".mkv", self.OutFile )
		OptionList										= []
		OptionList.append( 'HandBrakeCLI' )
		OptionList.append( '--input "%s"' % ( self.InFile ) )
		OptionList.append( '--output "%s"' % ( self.OutFile ) )
		OptionList.append( '--format %s' % ( self.Format ) )
		OptionList.append( '--title %s' % ( self.Title ) )
		OptionList.append( '--angle %s' % ( self.Angle ) )
		OptionList.append( '--verbose %s' % ( self.Verbose ) )
		OptionList.append( '--use-opencl' )
		OptionList.append( '--use-hwd' )
		OptionList.append( '--optimize' )
		OptionList.append( '--strict-anamorphic' )
		OptionList.append( '--decomb' )
		OptionList.append( '--modulus %s' % ( self.Modulus ) )
		OptionList.append( '--encoder %s' % ( self.Encoder ) )
		OptionList.append( '--x264-preset %s' % ( self.Preset ) )
		OptionList.append( '--h264-profile %s' % ( self.Profile ) )
		OptionList.append( '--h264-level %s' % ( self.Level ) )
		OptionList.append( '--quality %s' % ( self.ConstQual ) )
		OptionList.append( '--%s' % ( self.FrameControl ) )
		OptionList										= self.AudioOptions( OptionList )
		OptionList										= self.SubtitleOptions( OptionList )
		if ( self.ChapterFile != "notset" ):
			if ( not self.ChapterList == False ):
				OptionList.append( '--chapters 1-%s' % ( self.ChapterCount ) )
				OptionList.append( '--markers "%s"' % ( self.ChapterFile ) )
		self.Command									= ' '.join( str( Option ) for Option in OptionList )
		print( self.Command )
###------------------------------------------------------------------------------------------------------------------------------
