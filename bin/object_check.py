#!/usr/bin/python3
#-*-coding:utf8-*-

import json

_ = json.dumps

"""
1. 必需字段
2. 可选字段
3. 必须出现n次字段
4. 依赖字段
5. 类型检测
6. 值检测
7. 长度检测
"""

Optional = "optional"
Required = "required"
Appear   = "appear"
RelyOn   = "relyon"

SupportType = [ Optional,Required, Appear, RelyOn ]

class TemplateErr( Exception ):

    def __init__( self, logmsg ):
        super().__init__( logmsg )

class CheckTypeFail( Exception ):
    def __init__( self, logmsg ):
        super().__init__( logmsg )

class TemplateMismatchError( Exception ):
    def __init__( self, logmsg ):
        super().__init__( logmsg )

class UnsupportTypeChecker( Exception ):
    def __init__( self, logmsg ):
        super().__init__( logmsg )

class DependencyCheckFailed( Exception ):
    def __init__( self, logmsg ):
        super().__init__( logmsg )

class TemplateParser( object ):

    def __init__( self, log=print ):

        self.log = log

        self.appear_list    =   []
        self.optional_list  =   []
        self.required_list  =   []
        self.relyon_list    =   []
        self.str_2_dict     =   {}

        self.target_type_list = {
                Appear:     self.appear_list,
                Optional:   self.optional_list,
                Required:   self.required_list,
                RelyOn:     self.relyon_list,
                }

    def try_to_dict( self, string ):
        try:
            return json.loads( string )
        except Exception as e:
            self.log('[err]: '+str(e))
            pass
        return string

    def str_parser( self, key, value):
        if value in SupportType:
            key = [self.try_to_dict(key)]
            if type(key[0]) == dict:
                self.str_2_dict.update( key[0] )
            self.target_type_list[value].extend(key)
            return

        self.template_error( value )

    def dict_parser( self, key, value ):
        if len(value) != 1:
            return self.template_error( value )

        return self.select_dict_parser( key, value )

    def select_dict_parser( self, key, dict_obj ):
        for k, v in dict_obj.items():
            if k not in SupportType:
                raise TemplateErr(dict_obj)

            key = self.try_to_dict(key)

            # key 可以展开成dict的,保存进str_2_dict, 后期有用
            if type(key) == dict:
                self.str_2_dict.update( key )

            # tuple 可以作为key,不需要转成字符串
            if type(key) == tuple:
                self.target_type_list[k].append({ key: dict_obj[k] })
                continue

            # dict不可以作为key,需要转成字符串
            self.target_type_list[k].append({ json.dumps(key): dict_obj[k] })

    def template_error( self, key, value ):
        raise TemplateErr("declaration error in key:'{0}' value:'{1}'".format(key, value))

    def select_declaration_parser(self, value):

        self.parser_dict = {
                str: self.str_parser,
                dict: self.dict_parser,
                }

        self.parser_dict.setdefault( type( value ), self.template_error )

        return self.parser_dict[type(value)]

    def parse_template( self, template ):

        for key, value in template.items():
            parser = self.select_declaration_parser( value )
            parser( key, value )

    def print_target_field( self ):
        self.log('\nDeclaration filed:\n')
        for declaration, target_field in self.target_type_list.items():
            self.log( str(declaration) + ': ' + str(target_field) )

class ObjChecker( TemplateParser ):

    def __init__( self, log=print ):
        super( ObjChecker, self ).__init__( log )
        self.log = log
        pass

    def is_iterable( self, obj ):
        try:
            iter(obj)
            return True
        except TypeError:
            return False

    def check_type( self, obj, target_type, msg=None ):
        if type(obj) not in target_type:
            if msg: raise CheckTypeFail(msg)
            raise CheckTypeFail( 'Current type is {0} but target_type is: {1}'.format( type(obj), target_type ) )

    def unsupport_type_checker_error( self, compare_obj, field ):
        raise UnsupportTypeChecker( 'Unsupported Type For Field: "{0}" Type={1}'.format(field, type(field))  )

    def optional_str_field_checker( self, compare_obj, str_field  ):

        if not self.is_iterable( compare_obj ) or str_field not in compare_obj:
            self.log( '[nor]: Optional Field "{0}" Not Found In Compare Obj'.format(str_field) )
            return

        self.log( '[nor]: Optional Field "{0}" Has Found In Compare Obj'.format(str_field) )

    def optional_tuple_field_checker( self, compare_obj, tuple_field ):

        for field in tuple_field:
            if field in compare_obj:
                self.log( '[nor]: Optional Field "{0}" Has Found In Compare Obj'.format(field) )
                continue

            self.log( '[nor]: Optional Field "{0}" Not Found In Compare Obj'.format(field) )

    def optional_dict_field_checker( self, compare_obj, optional_dict_field ):

        for field, value in optional_dict_field.items():
            if field not in compare_obj:
                self.log( '[nor]: Optional Field <{0}> Not Found In Compare Obj'.format(field) )
            else:
                self.is_sub_satisfy( compare_obj, field )

    def optional_checker( self, template, compare_obj, path ):
        self.checker( template, compare_obj, Optional, path )

    def required_str_field_checker( self, compare_obj, required_field ):

        if not self.is_iterable( compare_obj ) or required_field not in compare_obj:
            raise TemplateMismatchError('Missing required field: "{0}"'.format(required_field))

        self.log('[suc]: Required Field "{0}" Found In Compare Obj'.format(required_field))

    def required_dict_field_checker( self, compare_obj, required_dict_field ):
        for field, value in required_dict_field.items():
            self.log('[log]: field: {0} value:{1}'.format(field, value) )
            if field not in compare_obj:
                raise TemplateMismatchError('Missing required field: "{0}"'.format(field))

            self.is_sub_satisfy( compare_obj, field )

    def required_tuple_field_checker( self, compare_obj, required_tuple_field ):

        for field in required_tuple_field:

            if field not in compare_obj:
                raise TemplateMismatchError('Missing required field: "{0}"'.format(field))

            self.log('[suc]: Requreid field "{0}" found in compare obj'.format(field))

    def required_checker( self, template, compare_obj, path ):
        self.checker( template, compare_obj, Required, path )

    def appear_str_field_checker( self, compare_obj, appear_field ):
        pass

    def appear_tuple_field_checker( self, compare_obj, appear_field, target_appear_time ):
        pass

    def appear_dict_field_checker( self, compare_obj, appear_field ):

        for field, value in appear_field.items():
            self.log('Checking appear field {0} value={1}'.format(field, value))
            target = self.try_to_dict( field )
            target_appear_time = value
            found_field = []
            appear_time = 0

            msg = "'Appear' keyword can only indicate dict/tuple field! "
            msg += 'but current field is:{0} type={1}'.format(field, type(field))

            self.check_type( target, [ dict, tuple ], msg )
            self.log('[log]: target:{0} type={1}'.format(target, type(target)))

            for k in target:
                if k in compare_obj:
                    found_field.append( k )
                    appear_time += 1

            if appear_time != target_appear_time:
                raise TemplateMismatchError(\
                        '[err]: Appear field: "{0}" mismatch, found_field:{1} appear_time={2} but target_appear_time={3}'\
                        .format(appear_field, found_field, appear_time, target_appear_time))

            self.log('[log]: Found appear filed: "{0}"'.format(found_field))

            if type(target) == tuple: continue

            for field in found_field:
                self.is_sub_satisfy( compare_obj, field, compare_obj )

    def appear_checker( self, template, compare_obj, path ):
        self.checker( template, compare_obj, Appear, path )

    def dependency_cheker( self, compare_obj, dependency ):

        self.log( 'Starting dependency: {0} check. compare_obj:{1}'.format(dependency, compare_obj) )
        self.check_type( dependency, [ dict ] )

        sub_compare_obj = compare_obj
        for k, v in dependency.items():
            self.log('Condition key:{0} value:{1}'.format(k, v))
            if k not in sub_compare_obj:
                raise DependencyCheckFailed('Dependency:{0} is not math compare_obj:{1}. key:{2} not found'\
                        .format(dependency, sub_compare_obj, k))

            if type(v) == dict:
                sub_compare_obj = sub_compare_obj[k]
                self.dependency_cheker( sub_compare_obj, v )
                continue

            if v != sub_compare_obj[k]:
                raise DependencyCheckFailed('Dependency:{0} is not math. ' \
                        'sub_compare_obj[{1}]={2}. but dependency[{3}]={4}'\
                        .format(dependency, k, sub_compare_obj[k], k, dependency[k]))

    def relyon_str_field_checker( self, compare_obj, relyon_field ):
        pass

    def relyon_tuple_field_checker( self, compare_obj, relyon_field ):

        for field in relyon_field:
            if field not in compare_obj:
                raise TemplateMismatchError('Field: {0} not found in compare_obj'.format(field))

            self.log('Found target field: "{0}" in compare_obj'.format(field))

    def relyon_dict_field_checker( self, compare_obj, relyon_field ):

        for field, dependency in relyon_field.items():
            self.log('[log]: field:{0} compare_obj:{1} dependency:{2}'.format(field, compare_obj, dependency))

            target_field = self.try_to_dict( field )
            self.check_type( target_field, [ dict, tuple ] )

            self.dependency_cheker( compare_obj, dependency )

            if type(target_field) == tuple:
                self.relyon_tuple_field_checker( compare_obj, target_field )
                continue

            self.log('[log]: dependency check pass, next check field:{0}'.format(target_field))

            for k, v in target_field.items():
                if k not in compare_obj:
                    raise TemplateMismatchError('Rely on field: "{0}" not found in compare obj: "{1}"'\
                            .format(k, compare_obj))

                if type(v) == str:
                    self.log('RelyOn field: "{0}" found in compare_obj'.format(k))
                    continue

                self.log('k:{0} v:{1}'.format(k, v))
                self.is_sub_satisfy( compare_obj, k )

    def relyon_checker( self, template, compare_obj, path ):
        self.checker( template, compare_obj, RelyOn, path )

    def checker( self, template, compare_obj, target_type, path ):

        if target_type not in SupportType:
            raise UnsupportTypeChecker('The target_type checker: "{0}" is not implemented'.format(target_type))

        type_list = "self." + target_type + '_list'
        type_field_checker = {
                str:    eval('self.'+ target_type + '_str_field_checker'),
                tuple:  eval('self.'+ target_type + '_tuple_field_checker'),
                dict:   eval('self.'+ target_type + '_dict_field_checker'),
                }

        for field in eval(type_list):
            self.log('[log]: Checking field: "{0}", type={1}, decla:{2}'.format(field, type(field), target_type))
            type_field_checker.setdefault( type(field), self.unsupport_type_checker_error )
            target_checker = type_field_checker[type(field)]
            target_checker( compare_obj, field, path )

    def is_sub_satisfy( self, compare_obj, field, sub_compare_obj=None, path=None ):

        sub_template = self.str_2_dict[field]

        if sub_compare_obj is None:
            sub_compare_obj = compare_obj[field]

        self.log( '[log]: sub template: {0} sub_compare_obj: {1}'.format(sub_template, sub_compare_obj) )
        ObjChecker(self.log).is_satisfy( sub_template, sub_compare_obj )

    def is_satisfy( self, template, compare_obj, path='' ):

        self.log("is_satisfy: \ntemplate:{0} \ncompare_obj:{1}".format(template, compare_obj))

        self.parse_template( template )
        self.print_target_field()
        self.log()

        self.checker( template, compare_obj, 'appear' )

        self.required_checker( template, compare_obj, path )
        self.appear_checker  ( template, compare_obj, path )
        self.optional_checker( template, compare_obj, path )
        self.relyon_checker  ( template, compare_obj, path )

def main():
    oc = ObjChecker()
    template = {
            "modify_attribute": Required,
            "common": Required,
            _({
                "status": {
                    "feed_status": Required,
                    },
                "rank": {
                    "rate": Required,
                    },
                "star":{
                    "dream": 1
                    },
                }): { Appear: 2 },

            _({"dict_required_field": {
                "some_field_optional": Optional,
                "some_field_required": Required,
                }}): Required,

            _({
                "optional_field2": {
                    "inner_required": Required,
                    },
                }): Optional,

            _({"relyon_item_field":{
                "some_item": Required,
                _({
                    "relyon_item_inner":{
                        "relyon_item_inner_required": Required,
                        }
                    }):{RelyOn: {
                        "relyon_item_field": {
                            "inner_pre_condition": 1,
                            },
                        }},
                }}) : { RelyOn: {
                    "common": {
                        "status":{
                            "feed_id": 110,
                            }
                    }} },

                _({
                    "rely_on_item": Required,
                    }):
                { RelyOn:{
                    "modify_attribute": 2,
                    }},

            ( "annother",  "required", "item", "in", "here" ): Required,

            ( "1", "2", "3", "4" ): Optional,

            _({"option-item": {},
                "option-item-2":{}
            }): Optional,

            ('another-appear-field', 'another-appear-field-2'): {Appear: 1},

            _({ "test2":{
                _({ "test3":{
                        "test4": Optional,
                        "test5": Required,
                        }
                    }): Optional,
                }
            }):Optional,

            (100, 102, 102) : { 
                    RelyOn : {
                        "modify_attribute": 2
                    } 
                }
        }

    compare_obj = {

            "optional_field2": {
                "inner_required": 1,
                },

            "modify_attribute": 2,

            "common":{
                "status":{
                "feed_id":110,
                }},
            "dict_required_field": {
                "some_field_required": 1,
                },
            "annother": 1,
            "required": 1,
            "item": 1,
            "in":2,
            "here":3,

            "status": {
                "feed_status": 1,
                },
            "rank": {
                "rate": 1,
                },

            "option-item": 2,
            "another-appear-field": 1,
            "test2": {
                "test3":{
                    "test5":1
                    }
                },
            'rely_on_item': {
                'some_item': 1,
                },
            'relyon_item_field': {
                'some_item': 1,
                'relyon_item_inner': {
                    "relyon_item_inner_required": 1,
                    },
                },
            100:1,
            102:1,
            103:1,
            }

    oc.is_satisfy( template, compare_obj )

if __name__ == '__main__':
    main()
