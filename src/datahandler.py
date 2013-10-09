import	codecs
import	os

###------------------------------------------------------------------------------------------------------------------------------
class DataHandler():
	def __init__( self, filename ):
		self.data									= []
		self.filename								= filename
		#if ( os.path.isfile( self.filename ) ):
	#----------------------------------------------------------------------------------------------------------------------
	def OpenFile( self ):
		import codecs
		try:
			if ( os.path.isfile( self.filename ) ):
				self.WriteHDL						= codecs.open( self.filename, mode="a", encoding="utf-8" )
			else:
				self.WriteHDL						= codecs.open( self.filename, mode="w", encoding="utf-8" )
		except:
			print( "Error opening %s for writing!" % self.filename )
	#----------------------------------------------------------------------------------------------------------------------
	def CloseFile( self ):
			self.WriteHDL.close()
	#----------------------------------------------------------------------------------------------------------------------
	def Append( self, data ):
		try:
			WriteHDL								= codecs.open( self.filename, mode="a", encoding="utf-8" )
		except:
			try:
				self.Write( data )
			except:
				print( "Error writing to file %s!" % self.filename )
		else:
			try:
				WriteHDL.write( '%s\n' % ( data ) )
			except Exception, e:
				print( "Error writing to file %s.\tActual: %s" % ( self.filename, e ) )
			WriteHDL.close()
	#----------------------------------------------------------------------------------------------------------------------
	def Read( self ):
		ReadHDL										= codecs.open( self.filename, mode="r", encoding="utf-8" )
		for line in ReadHDL.readlines():
			line									= line.rstrip()
			self.data.append( line )
		self.data									= list(set( self.data ))
		ReadHDL.close()
	#----------------------------------------------------------------------------------------------------------------------
	def Write( self, data ):
		if ( not os.path.isfile( self.filename ) ):
			try:
				WriteHDL								= codecs.open( self.filename, mode="w", encoding="utf-8" )
			except:
				try:
					self.Append( data )
				except:
					print( "Error opening %s for writing!" % self.filename )
			else:
				try:
					WriteHDL.write( '%s\n' % ( data ) )
				except Exception, e:
					print( "Error writing to file %s.\tActual: %s" % ( self.filename, e ) )
				WriteHDL.close()
		else:
			self.Append( data )
	#----------------------------------------------------------------------------------------------------------------------
	def data( self ):	
		return self.data
		#dataHandle										= DataHandler( file )