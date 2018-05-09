# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser

# 扩展默认的auth_user表的字段类型
class UserProfile(AbstractUser):
    '''
    用户信息，继承了基础用户表
    '''
    nick_name = models.CharField(max_length=50,verbose_name=u'昵称',default=u'')
    birthday = models.DateField(verbose_name=u'生日',null=True,blank=True) #blank 是针对表单的，如果 blank=True，表示你的表单填写该字段的时候可以不填，比如 admin 界面下增加 model 一条记录的时候。直观的看到就是该字段不是粗体
    gender = models.CharField(max_length=7,choices=(('male',u'男'),('female',u'女')),default='female')
    address = models.CharField(max_length=100,default=u'')
    mobile = models.CharField(max_length=11,null=True,blank=True)
    image = models.ImageField(upload_to='image/%Y/%m',default=u'image/default.png',max_length=100)


    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username