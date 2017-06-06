import numpy as np

__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-06-02"
__version__="1.0-dev"


class _Envelope(object):
		def __init__(self):
				self.__capa=0
				self.__theta=0.0005
				self.__limit =10

		def  UpperSlope(self,data):
			data=np.array(np.absolute(data))
			for i in range(len(data)):
				if ( self.__capa >= self.__limit):
					self.__capa =0
				elif (self.__capa <= data[i]):
					self.__capa = data[i]
				
				elif (self.__capa <=0 ) :
					self.__capa =0
				else :
					self.__capa = self.__capa - self.__theta
			return self.__capa
		def initialize(self):
				self.__capa=0
