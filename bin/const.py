#!/usr/bin/python3
#-*-coding:utf8-*-

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

CommonType  = [ int, float, str, bool ]
