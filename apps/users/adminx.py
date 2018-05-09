# -*- coding:utf-8 -*-

import xadmin
from .models import UserProfile

import xadmin
#额外的主题修改
from xadmin import views


# xadmin进阶配置,最新的已经不需要了
# from xadmin.plugins.auth import UserAdmin
# from .models import UserProfile
#
# class UserProfileAdmin(UserAdmin):
#     pass
#
# xadmin.site.register(UserProfile,UserProfileAdmin)

#全局设置
class GlobalSettings(object):
    site_title = "NWSJ管理系统 "    #Logo
    site_footer = '纳维世纪后台管理系统'   #网页页脚信息
    menu_style = 'accordion'    #右侧导航栏折叠功能


xadmin.site.register(views.CommAdminView,GlobalSettings)
#额外的主题修改
class BaseSetting(object):
    enable_themes = True    #表示使用主题功能
    use_bootswatch = True


xadmin.site.register(views.BaseAdminView,BaseSetting)
