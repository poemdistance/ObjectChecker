#!/usr/bin/python3
#-*-coding:utf8-*-

class CheckTypeFail( Exception ):
    def __init__( self, logmsg ):
        super().__init__( logmsg )

class Checker( object ):
    def __init__( self ):
        pass

    def check_type( self, obj, target_type ):
        if type(obj) not in target_type:
            raise CheckTypeFail('Target type is: {0} but now is: {1}'.\
                    format(target_type, type(obj)))
        return True
