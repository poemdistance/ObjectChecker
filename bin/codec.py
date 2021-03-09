#!/usr/bin/python3
#-*- coding: utf8 -*-

import json
from const import *
from adinUtils import *

"""
dumps 需要解决的问题:
    1. 知道要使用哪个encoder, 将不可dumps的对象转成可dumps对象

load 需要解决的问题:
    1. 从原始加载对象中,解析出目标decoder,初始化出源对象.

综上,需要将encoder和decoder都存入序列化对象中,并且能够通过某种方式找出encoder和decoder

Code提供基本的encoder和decoder,对于一些类型提供基础支持,不支持的情况下,需要用户自己传入自己
的encoder和decoder.
"""

TmpValue = {}

class Complex( object ):
    def __init__( self, a=0, b=0 ):
        self.a = a
        self.b = b
        self.complex = complex( self.a, self.b )

class Codec( object ):

    def __init__( self, encode_selector={}, decode_selector={} ):
        self.encode_selector = encode_selector
        self.decode_selector = decode_selector
        pass

    def key_with_type( self, key ):
        return str({ "key": key, "type": type(key) })

    def encode( self, obj, result, pre_key='' ):

        if type(obj) in CommonType: 
            return obj

        Checker().check_type( obj, [dict] )

        for key, value in obj.items():
            key_type = type( key )
            value_type = type( value )
            if key_type in CommonType and value_type == dict:
                key_with_type  = self.key_with_type( key )
                result.update( { key_with_type : TmpValue } )
                self.encode( value, result, key_with_type )
                continue

            if key_type in CommonType and value_type in CommonType:
                result[pre_key].update( { key : value } )
                continue

            # TODO
            # if key_type in CommonType and value_type in ObjectType:

            """
            {
                codec.dumps({}) as str:  set / class / CommonType / dict
                CommonType:              set / class / CommonType / dict
                class:                   set / class / CommonType / dict
                set:                     set / class / CommonType / dict
            }
            """


    def decode( self, obj, result ):
        pass


    def dumps( self, obj ):
        Checker().check_type( obj, [dict] )
        result = {}
        self.encode( obj, result )
        print('dumps result: ' + str(result))

    def load( self, obj ):
        result = {}
        self.decode( obj, result )
        print('load result: ' + str(result))

def main():

    c = Complex()
    c.complex = complex(1, 2)

    codec = Codec();

    d = { 
            codec.dumps( {

                1: {
                    2: Required
                    }

                }): Optional
        }

    codec.dumps(d)

if __name__ == '__main__':
    main()
