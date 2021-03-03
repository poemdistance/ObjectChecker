#!/usr/bin/python3
#-*-coding:utf8-*-

s = { 1, 2, 3, 4 }
l = [1, 2, 3, 5, 6, 76]

print({ i for i in s if i not in l })
