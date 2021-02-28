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

SupportType = [ Optional, Required, Appear, RelyOn ]

class TemplateErr( Exception ):

    def __init__( self, logmsg ):
        super().__init__( logmsg )

class CheckTypeFail( Exception ):
    def __init__( self, logmsg ):
        super().__init__( logmsg )

class TemplateMismatchError( Exception ):
    def __init__( self, declaration, path, field, logmsg=None ):

        if logmsg is None and len(path) > 0:
            path = 'root.' + '.'.join( str(i) for i in path )
            logmsg = 'Missing {0} field: "{1}.{2}"'.format(declaration, path, field )
        elif logmsg is None:
            logmsg = 'Missing {0} field: "{1}"'.format(declaration, field )

        super().__init__( logmsg )

class UnsupportTypeChecker( Exception ):
    def __init__( self, logmsg ):
        super().__init__( logmsg )

class DependencyCheckFailed( Exception ):
    def __init__(  self, compare_obj, dependency, path, field, err_type='not found' ):


        if err_type == 'not found' and len(path) > 0:
            path = '.'.join( str(i) for i in path )
            logmsg = 'Dependency mismatch, key: "{0}.{1}" not found.'.format(path, field)

        elif err_type == 'not found' and len(path) <= 0:
            logmsg = 'Dependency mismatch, key: "{0}" not found.'.format(field)

        elif err_type == 'condition err' and len(path) > 0:
            full_path = 'compare_obj'
            for node in path:
                if type(node) != str:
                    full_path += '['+str(node) +']'
                else:
                    full_path += "['"+node +"']"

                compare_obj = compare_obj[node]
                dependency = dependency[node]

            logmsg = 'Dependency mismatch, target is "{0}={1}" but now is "{2}"'.\
                    format(full_path, dependency, compare_obj )

        elif err_type == 'condition err' and len(path) <= 0:
            full_path = 'compare_obj[{0}]'.format(field)
            logmsg = 'Dependency mismatch, target is "{0}={1}" but now is "{2}"'.\
                    format(full_path, dependency[field], compare_obj[field] )
        else:
            pass

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

    def copy_list( self, list_obj ):

        result = []
        for item in list_obj:
            result.append( item )

        return result

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

    def print_dependency_result( self, dependency, field, is_pass=True ):
        if is_pass:
            self.log('The dependency <{0}> of field: {1} pass check'.format(dependency, field))
        else:
            self.log('The dependency <{0}> of field: {1} not satisfy '.format(dependency, field))

    def print_message( self, declaration, path, field, found=True ):

        result = 'found' if found else 'not found'
        if len(path) <= 0:
            self.log('{0} field "{1}" {2} in compare_obj'.format(declaration, field, result))
            return

        self.log('{0} field "{1}.{2}" {3} in compare_obj'.format(declaration, path, field, result))

    def get_sub_obj( self, obj, path ):

        if len(path) == 0:
            return obj

        for node in path:
            obj = obj[node]

        return obj


    def get_sub_compare_obj( self, compare_obj, path ):
        return self.get_sub_obj( compare_obj, path )

    def get_sub_dependency( self, dependency, path ):
        return self.get_sub_obj( dependency, path )

    def optional_str_field_checker( self, compare_obj, str_field, current_path  ):

        if not self.is_iterable( compare_obj ) or str_field not in compare_obj:
            self.print_message(Optional, current_path, str_field)
            return

        self.print_message(Optional, current_path, str_field, found=False)

    def optional_tuple_field_checker( self, compare_obj, tuple_field, current_path ):

        for field in tuple_field:
            if field in compare_obj:
                self.print_message(Optional, current_path, field)
                continue

            self.print_message( Optional, current_path, field, found=False )

    def optional_dict_field_checker( self, compare_obj, optional_dict_field, current_path ):

        for field, value in optional_dict_field.items():
            if field not in compare_obj:
                self.print_message(Optional, current_path, field, found=False)
            else:
                local_path = self.copy_list( current_path )
                local_path.append( field )
                self.is_sub_satisfy( compare_obj, field, path=local_path)

    def optional_checker( self, template, compare_obj, current_path ):
        self.checker( template, compare_obj, Optional, current_path )

    def required_str_field_checker( self, compare_obj, required_field, current_path ):

        sub_compare_obj = self.get_sub_compare_obj( compare_obj, current_path )

        if not self.is_iterable( sub_compare_obj ) or required_field not in sub_compare_obj:
            raise TemplateMismatchError( Required, current_path, required_field )

        self.print_message(Required, current_path, required_field)

    def required_dict_field_checker( self, compare_obj, required_dict_field, current_path ):
        sub_compare_obj = self.get_sub_compare_obj( compare_obj, current_path )
        for field, value in required_dict_field.items():
            if field not in sub_compare_obj:
                raise TemplateMismatchError( Required, current_path, field )

            local_path = self.copy_list( current_path )
            local_path.append( field )
            self.is_sub_satisfy( compare_obj, field, path=local_path )

    def required_tuple_field_checker( self, compare_obj, required_tuple_field, current_path ):

        sub_compare_obj = self.get_sub_compare_obj( compare_obj, current_path )

        for field in required_tuple_field:
            if field not in sub_compare_obj:
                raise TemplateMismatchError( Required, current_path, field )

            self.print_message(Required, current_path, field)

    def required_checker( self, template, compare_obj, current_path ):
        self.checker( template, compare_obj, Required, current_path )

    def appear_str_field_checker( self, compare_obj, appear_field, current_path ):
        pass

    def appear_tuple_field_checker( self, compare_obj, appear_field, target_appear_time ):
        pass

    def appear_dict_field_checker( self, compare_obj, appear_field, current_path ):

        for field, value in appear_field.items():
            target = self.try_to_dict( field )
            target_appear_time = value
            found_field = []
            appear_time = 0

            msg = "'Appear' keyword can only indicate dict/tuple field! "
            msg += 'but current field is:{0} type={1}'.format(field, type(field))

            self.check_type( target, [ dict, tuple ], msg )

            for k in target:
                if k in compare_obj:
                    found_field.append( k )
                    appear_time += 1

            if appear_time != target_appear_time:
                raise TemplateMismatchError(logmsg=\
                        'Appear field: "{0}" mismatch, found_field:{1} appear_time={2} but target_appear_time={3}'\
                        .format(appear_field, found_field, appear_time, target_appear_time))

            self.print_message(Appear, current_path, found_field)

            if type(target) == tuple: continue

            for field in found_field:
                local_path = self.copy_list( current_path )
                local_path.append( field )
                self.is_sub_satisfy( compare_obj, field, path=local_path )

    def appear_checker( self, template, compare_obj, current_path ):
        self.checker( template, compare_obj, Appear, current_path )

    def dependency_cheker( self, compare_obj, dependency, current_path ):

        self.check_type( dependency, [ dict ] )

        sub_dependency = self.get_sub_dependency( dependency, current_path )

        self.check_type( sub_dependency, [ dict ] )

        for k, v in sub_dependency.items():
            sub_compare_obj = self.get_sub_compare_obj(compare_obj, current_path)
            if not self.is_iterable(sub_compare_obj) or k not in sub_compare_obj:
                raise DependencyCheckFailed( compare_obj, dependency, current_path, k )

            if type(v) == dict:
                local_path = self.copy_list( current_path )
                local_path.append( k )
                self.dependency_cheker( compare_obj, dependency, local_path )

    def relyon_str_field_checker( self, compare_obj, relyon_field, current_path ):
        pass

    def relyon_tuple_field_checker( self, compare_obj, relyon_field, current_path ):

        for field in relyon_field:
            if field not in compare_obj:
                raise TemplateMismatchError(RelyOn, current_path, field)

            self.print_message( RelyOn, current_path, field )

    def relyon_dict_field_checker( self, compare_obj, relyon_field, current_path ):

        for field, dependency in relyon_field.items():

            target_field = self.try_to_dict( field )
            self.check_type( target_field, [ dict, tuple ] )

            self.dependency_cheker( compare_obj, dependency, [] )

            if type(target_field) == tuple:
                self.relyon_tuple_field_checker( compare_obj, target_field, current_path )
                continue

            sub_compare_obj = self.get_sub_compare_obj( compare_obj, current_path )

            for k, v in target_field.items():
                if k not in sub_compare_obj:
                    raise TemplateMismatchError( RelyOn, current_path, k )

                if type(v) == str:
                    self.print_message( RelyOn, current_path, k )
                    continue

                local_path = self.copy_list( current_path )
                local_path.append( k )
                self.is_sub_satisfy( compare_obj, k, path=local_path )

    def relyon_checker( self, template, compare_obj, current_path ):
        self.checker( template, compare_obj, RelyOn, current_path )

    def checker( self, template, compare_obj, target_type, current_path ):

        if target_type not in SupportType:
            raise UnsupportTypeChecker('The target_type checker: "{0}" is not implemented'.format(target_type))

        type_list = "self." + target_type + '_list'
        type_field_checker = {
                str:    eval('self.'+ target_type + '_str_field_checker'),
                tuple:  eval('self.'+ target_type + '_tuple_field_checker'),
                dict:   eval('self.'+ target_type + '_dict_field_checker'),
                }

        for field in eval(type_list):
            type_field_checker.setdefault( type(field), self.unsupport_type_checker_error )
            target_checker = type_field_checker[type(field)]
            target_checker( compare_obj, field, current_path )

    def is_sub_satisfy( self, compare_obj, field, path=[] ):

        sub_template = self.str_2_dict[field]
        sub_compare_obj = compare_obj

        ObjChecker(self.log).is_satisfy( sub_template, sub_compare_obj, path )

    def is_satisfy( self, template, compare_obj, path=[] ):

        self.parse_template( template )
        # self.print_target_field()
        # self.log()

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
                }): Required,
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

            "modify_attribute": 1,

            "common":{
                },
            "dict_required_field": {
                "some_field_required": 1,
                },
            "annother": 1,
            "required": 1,
            "item": 1,
            "in":2,
            "here":3,

            "option-item": 2,
            "another-appear-field": 1,
            "test2": {
                "test3":{
                    "test5":1,
                    },
                },
            'rely_on_item': {
                'some_item': 1,
                },
            'relyon_item_field': {
                'some_item': 1,
                'inner_pre_condition': True,
                'relyon_item_inner': {
                    "relyon_item_inner_required": 1,
                    },
                },
            100:1,
            102:1,
            103:1,

            "status": {
                'feed_status': 1,
                },
            "rank": {
                "rate": 1,
                },
            "common": {
                "status":{
                    "feed_id": 110,
                    },
                },
            }

    oc.is_satisfy( template, compare_obj )

if __name__ == '__main__':
    main()
