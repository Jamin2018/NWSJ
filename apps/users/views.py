# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate,login,logout  #django自带认证模块
from .forms import LoginForm
import json
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


@csrf_exempt
def LoginView(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)  # 成功返回user对象，失败返回None
        if user:
            # print('用户存在')
            if user.is_active:
                login(request, user)
                # return HttpResponse(json.dumps({"err": 0, "msg": "登录成功"}), content_type='application/json')
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse(json.dumps({"err": -1, "msg": u"该用户未激活!"}),content_type='application/json')
        else:
            return HttpResponse(json.dumps({"err": -1, "msg": u"用户名或密码错误!"}), content_type='application/json')


def LogoutView(request):
    if request.method == 'GET':
        logout(request)
        from django.core.urlresolvers import reverse
        return HttpResponseRedirect(reverse('index'))