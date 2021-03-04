#!/usr/bin/python
#-*- coding: utf8 -*-

import unittest

from object_check import *


class TestObjChecker(unittest.TestCase):

    def test_required_check_succ( self ):

        template = { 
                'str'   :   Required,
                1       :   Required,   
                2.1     :   Required, 
                1+1j    :   Required,
                }

        compare_obj = {
                'str'   :   1,
                1       :   1,
                2.1     :   1,
                1+1j    :   1,
                }

        ObjChecker().is_satisfy( template, compare_obj )

    def test_required_check_fail( self ):

        template = { 
                'str'   :   Required,
                1       :   Required,   
                2.1     :   Required, 
                1+1j    :   Required,
                }

        compare_obj = {
                'str'   :   1,
                1       :   1,
                1+1j    :   1,
                }

        with self.assertRaises( TemplateMismatchError ):
            ObjChecker().is_satisfy( template, compare_obj )

    def test_optional_check_succ( self ):

        template = { 
                'str'   :   Optional,
                1       :   Optional,   
                2.1     :   Optional, 
                1+1j    :   Optional,
                }

        compare_obj = {
                'str'   :   1,
                1+1j    :   1,
                }

        ObjChecker().is_satisfy( template, compare_obj )

    def test_appear_check_succ( self ):

        template = { 
                    json.dumps({
                        'need_to_appear1': {

                            },
                        'need_to_appear2': {

                            },
                        'need_to_appear3': {

                            }
                        }): { Appear : 2 }
                }

        compare_obj = {
                'need_to_appear1': {
                    1:  1
                    },
                'need_to_appear2': {
                    2:  2
                    },
                }

        ObjChecker().is_satisfy( template, compare_obj )

    def test_appear_check_fail( self ):

        template = { 
                    json.dumps({
                        'need_to_appear1': {

                            },
                        'need_to_appear2': {

                            },
                        'need_to_appear3': {

                            }
                        }): { Appear : 2 }
                }

        compare_obj = {
                'need_to_appear1': {
                    1:  1
                    },
                }

        with self.assertRaises( TemplateMismatchError ): 
            ObjChecker().is_satisfy( template, compare_obj )

    def test_relyon_check_succ0( self ):

        template = {
                json.dumps({
                    'be_relyon_field': {
                        'inner': Required,
                        }
                    }): Optional,

                'rely_on_field': {
                    RelyOn: 'be_relyon_field'
                    }
                }

        compare_obj = {
                }

        ObjChecker().is_satisfy( template, compare_obj )

    def test_relyon_check_succ( self ):

        template = {
                json.dumps({
                    'be_relyon_field': {
                        'inner': Required,
                        }
                    }): Optional,

                'rely_on_field': {
                    RelyOn: 'be_relyon_field'
                    }
                }

        compare_obj = {
                    'be_relyon_field':  {
                        'inner': 2
                        },
                    'rely_on_field': 2
                }

        ObjChecker().is_satisfy( template, compare_obj )

    def test_relyon_check_succ1( self ):

        template = {
                json.dumps({
                    'be_relyon_field': {
                        'inner': Required,
                        }
                    }): Optional,

                'rely_on_field': {
                    RelyOn: { 'be_relyon_field': {
                        'inner': 1+2j,
                        } }
                    }
                }

        compare_obj = {
                    'be_relyon_field':  {
                        'inner': 1+2j
                        },
                    'rely_on_field': 2
                }

        ObjChecker().is_satisfy( template, compare_obj )

    def test_relyon_check_succ2( self ):

        template = {

                'be_relyon_field': Optional,

                'rely_on_field': {
                    RelyOn: { 'be_relyon_field': 1 }
                    }
                }

        compare_obj = {
                    'be_relyon_field': 1,
                    'rely_on_field': 2
                }

        ObjChecker().is_satisfy( template, compare_obj )

    def test_relyon_check_succ3( self ):

        template = {

                'be_relyon_field': Optional,

                'rely_on_field': {
                    RelyOn: { 'be_relyon_field': 1 }
                    }
                }

        compare_obj = {
                    'be_relyon_field': 100,
                    'rely_on_field': 2
                }

        with self.assertRaises( TemplateMismatchError ):
            ObjChecker().is_satisfy( template, compare_obj )

    def test_relyon_check_fail0( self ):

        template = {
                json.dumps({
                    'be_relyon_field': {
                        'inner': Required,
                        }
                    }): Optional,

                'rely_on_field': {
                    RelyOn: { 'be_relyon_field': {
                        'inner': 1+2j,
                        } }
                    }
                }

        compare_obj = {
                    'be_relyon_field':  {
                        'inner': 1+2j
                        },
                    # 'rely_on_field': 2
                }

        with self.assertRaises( TemplateMismatchError ):
            ObjChecker().is_satisfy( template, compare_obj )

    def test_relyon_check_fail1( self ):

        template = {
                json.dumps({
                    'be_relyon_field': {
                        'inner': Required,
                        }
                    }): Optional,

                'rely_on_field': {
                    RelyOn: 'be_relyon_field'
                    }
                }

        compare_obj = {
                    'be_relyon_field':  {
                        'inner': 2
                        },
                }

        with self.assertRaises( TemplateMismatchError ):
            ObjChecker().is_satisfy( template, compare_obj )

    def test_relyon_check_fail2( self ):

        template = {
                json.dumps({
                    'be_relyon_field': {
                        'inner': Required,
                        }
                    }): Optional,

                'rely_on_field': {
                    RelyOn: 'be_relyon_field'
                    }
                }

        compare_obj = {
                    'be_relyon_field':  {
                        },
                }

        with self.assertRaises( TemplateMismatchError ):
            ObjChecker().is_satisfy( template, compare_obj )

    def test_relyon_check_fail2( self ):

        template = {
                json.dumps({
                    'be_relyon_field': {
                        'inner': Required,
                        }
                    }): Optional,

                'rely_on_field': {
                    RelyOn: 'be_relyon_field'
                    }
                }

        compare_obj = {
                    'be_relyon_field':  {
                        },
                }

        with self.assertRaises( TemplateMismatchError ):
            ObjChecker().is_satisfy( template, compare_obj )

    
    def test_large_condition_succ( self ):

        template = {
                "first-str-required-field": Required,
                1:                          Required,
                2.3:                        Required,
                1+2j:                       Required,

                'relyon-field':           { RelyOn : 1 },
                3:                        { RelyOn : 2.3 } ,

                json.dumps({

                    'more-than-one-depth': {
                        json.dumps({
                            'second-depth': {
                                'third-depth': Required,
                                },
                            }): Required
                        },

                    'more-than-one-depth2': {
                        json.dumps({
                            'second-depth': {
                                'third-depth': Required,
                                }
                            }): { RelyOn: {
                                "more-than-one-depth":{
                                    'second-depth':{
                                        'third-depth': 1,
                                        's': 2
                                        },
                                    'second-depth2': 5
                                    },
                                } } ,
                        },

                    }): Required,

                json.dumps({

                    'optional-field1': {
                            json.dumps({
                            'optional-depth2':{}
                            }): Optional
                        },

                    'optional-field2': {

                        }

                    }): Optional,

                json.dumps({

                    'first-appear': {
                        'inner-appear-requied-field': Required,

                        json.dumps({
                            "required-in-appear": {
                                'good': Required
                                }
                            }): Required,

                        json.dumps({
                            'appear': { },
                            'appear2': { },

                            }): { Appear : 1 }
                        },

                    }) : { Appear : 1  },

                json.dumps({
                    'appear-relyon':{
                        'test':     Optional,
                        }
                    }):
                    { RelyOn :
                        {
                            'first-appear': {
                                'required-in-appear': {
                                    # 'good', 'study', 'day', 'up'
                                    }
                                }
                        }
                    }
                }

        compare_obj = {
                "first-str-required-field": 1,
                1:      1,
                2.3:    1,
                1+2j:   2,

                'relyon-field':         1,
                3:                      1,

                'more-than-one-depth': {
                    'second-depth': {
                        'third-depth': 1,
                        's': 3,
                        },
                    'second-depth2': 5
                },

                'more-than-one-depth2': {
                    'second-depth': {
                        'third-depth': 1,
                        }
                },

                'first-appear': {
                    'inner-appear-requied-field': 1,
                    'required-in-appear': {
                        'good': 2
                        },
                    'appear': {
                        'test': 2
                        },
                    },

                'appear-relyon': {

                    },
            }

        ObjChecker().is_satisfy( template, compare_obj )



if __name__ == '__main__':
    unittest.main()
