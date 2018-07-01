# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

import time
import math

from django.http import JsonResponse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, redirect, render

from Block import APBlock, DelayBlock, PBlock, IBlock

from scipy import signal

def alter_step(request):
    result = {}
    if request.method == 'POST':
        if request.POST.get('force_hold', '') != 'true':
            global step
            global timer
            global ap_block
            global p_block_regulator
            global i_block_regulator
            new_step = int(request.POST.get('value', 0))
            action = request.POST.get('action', '')
            if step != new_step:
            	step = new_step
                ap_block.step = step
                p_block_regulator.step = step
                i_block_regulator.step = step
            result['code'] = '200'
    return JsonResponse(result)


def alter_step_air(request):
    result = {}
    if request.method == 'POST':
        new_step = int(request.POST.get('value_air', 0))
        action = request.POST.get('action', '')
        if step_air != new_step:
        	step_air = new_step
        result['code'] = '200'
    return JsonResponse(result)


def alter_model_temp(request):
    result = {}
    if request.method == 'POST':
        if request.POST.get('force_hold', '') != 'true':
            global model_temp
            new_temp = int(request.POST.get('value', 1250))
            if new_temp < 0:
                model_temp = 0
            else:
                model_temp = new_temp
            result['code'] = '200'
    return JsonResponse(result)


def profile(request):
    global ap_block
    global delay_block
    global ap_block_air
    global i_block_regulator
    global p_block_regulator
    global step
    global step_air
    global step_regul
    global model_temp
    global timer
    global buff

    timer = 0.
    buff = [0,]
    delta = 1
    step = 20
    step_air = 200
    step_regul = 0
    model_temp = 125

    ap_block = APBlock(k=2, T=30, delta=delta, step=step) #3.4  7.29

    ap_block_air = APBlock(k=0.05, T=10, delta=delta, step=step_air)
    
    delay_block = DelayBlock(delay=10, delta=delta)

    p_block_regulator = PBlock(k=0.2, step=step_regul)

    i_block_regulator = IBlock(k=0.2, Ti=100, step=step_regul)

    return render(request, 'profile/index.html', {'step':step,
    											  'step_air':step_air,
                                                  'delta':delta})


def chart_model(request):
    if request.method == 'GET':
        global timer
        global delay_block
        global ap_block
        global ap_block_air
        global p_block_regulator
        global i_block_regulator
        global step_regul
        global step
        global step_air
        result = {}
        regul = (p_block_regulator + i_block_regulator).y
        step += regul
        step = 0 if step < 0 else step
        step_air = step * 10

        ap_block.step = step
        ap_block_air.step = step_air
        y_result = (ap_block * delay_block + ap_block_air).y
        y_result = 0. if y_result < 0 else y_result

        # zadanie - vihod
        step_regul = model_temp - y_result
        i_block_regulator.step = step_regul
        p_block_regulator.step = step_regul

        # vozmychenie - vihod
        # y_last = ap_block_air.y_values[-2] + delay_block.make_delay(position)
        # step_regul += y_result - y_last

        timer += ap_block.delta
        result['x'] = timer
        result['regul'] = step_regul
        result['y'] = y_result
        result['stepregul'] = step
        result['stepregul_air'] = step_air
        return JsonResponse(result)
    else:
        raise Http404()


def state_space(request):
    y2 = request.POST.get('y2')
    y1 = request.POST.get('y1')
    y = request.POST.get('y')
    u1 = request.POST.get('u1')
    u = request.POST.get('u')
    print(float(u1))
    print(float(y2))
    if float(y2) != 0.0:
        a1 = float(y1) / float(y2)
        a2 = float(y) / float(y2)
        b0 = 0
        b1 = float(u1) / float(y2)
        b2 = float(u) / float(y2)
        A = [[0.0, 1.0], [-a2, -a1]]
        B = [[b1 - a1 * b0], [b2 - a1 * (b1 - a1 * b0) - a2 * b0]]
        C = [1.0, 0.0]
        D = [0.0]
    else:
        A = -float(y) / float(y1)
        B = float(u) / float(y1) - float(y) / float(y1) * float(u1)
        C = 1.0
        D = 0.0
    sys = signal.StateSpace(A, B, C, D)
    x, y = signal.step(sys)
    x_values = [round(obj, 2) for obj in x]
    y_values = [round(obj, 2) for obj in y]
    return JsonResponse({'x':x_values,
                         'y':y_values})


def optimization(request):
    global delay_block
    global ap_block
    global ap_block_air
    global p_block_regulator
    global i_block_regulator
    global step_regul
    global step
    global step_air
    global buff

    while len(buff) < 400:
        regul = (p_block_regulator + i_block_regulator).y
        step += regul
        step = 0 if step < 0 else step
        step_air = step * 10
        ap_block.step = step
        ap_block_air.step = step_air
        y_result = (ap_block * delay_block + ap_block_air).y
        y_result = 0. if y_result < 0 else y_result
        # zadanie - vihod
        step_regul = model_temp - y_result
        i_block_regulator.step = step_regul
        p_block_regulator.step = step_regul
        buff.append(y_result)
    data = {'x':[x for x in range(0, 401)],
            'y':buff}
    #return HttpResponseRedirect(reverse('sq_integr'))
    return JsonResponse({'x':[x for x in range(0, 401)],
                         'y':buff})


def square_integral_metric(request):
    y_val = buff
    x_val = [x for x in range(0, len(buff) + 1)]
    result = 0
    for i in range(1, len(y_val)):
        result += ((model_temp - y_val[i]) * (x_val[i] - x_val[i - 1])) ** 2
    print(result)
    return JsonResponse({'y':y_val,
                         'x':x_val})


def coordinate_descent_optimize(request):
    global p_block_regulator
    global i_block_regulator
    global buff
    global i_curr
    global i_prev
    def process():
        global p_block_regulator
        global i_block_regulator
        global ap_block
        global ap_block_air
        global buff
        global delay_block
        global ap_block
        global ap_block_air
        delta = 1
        step = 20
        step_air = 200
        step_regul = 0
        model_temp = 125
        ap_block.step = step
        ap_block_air.step = step_air
        i_block_regulator.step = step_regul
        p_block_regulator.step = step_regul
        delay_block.y_values = [0,]
        ap_block.y_values = [0,]
        ap_block_air.y_values = [0,]
        buff = [0,]
        while len(buff) < 800:
            regul = (p_block_regulator + i_block_regulator).y
            step += regul
            if step < 0:
                step = 0
            #elif step > 100:
            #    step = 100
            step_air = step * 10
            ap_block.step = step
            ap_block_air.step = step_air
            y_result = (ap_block * delay_block + ap_block_air).y
            y_result = 0. if y_result < 0 else y_result
            # zadanie - vihod
            step_regul = model_temp - y_result
            i_block_regulator.step = step_regul
            p_block_regulator.step = step_regul
            buff.append(y_result)

    def sq_integr():
        result = 0
        for i in range(1, len(buff) - 1):
            result += (((model_temp - buff[i]) + (model_temp - buff[i+1])) / 2) ** 2
        return result

    def opt_k(plus, k_step):
        if plus:
            p_block_regulator.k += k_step
            i_block_regulator.k += k_step
        else:
            p_block_regulator.k -= k_step
            i_block_regulator.k -= k_step

    def opt_t(plus, T_step):
        if plus:
            i_block_regulator.Ti += T_step
        else:
            i_block_regulator.Ti -= T_step

    def optimization_k():
        global i_curr
        global i_prev
        k_step = 0.1
        process()
        i_curr = sq_integr()
        i_prev = i_curr
        way_counter = 0
        way = False
        while True:
            print(p_block_regulator.k)
            if i_curr - i_prev <= 0:
                opt_k(way, k_step)
                if k_step < 0.001:
                    break
                if p_block_regulator.k <= 0:
                    k_step /= 2
                    way = True
                    continue
                process()
                i_prev = i_curr
                i_curr = sq_integr()
            else:
                way = not way
                k_step /= 2
                opt_k(way, k_step)
                i_prev = i_curr
                process()
                i_curr = sq_integr()                
                if math.fabs(i_curr - i_prev) < 0.01:
                    break
            if math.fabs(i_curr - i_prev) < 0.01 and i_curr != i_prev:
                break
        print(i_curr, 'integr with opt K')
    
    def optimization_T():
        global i_curr
        global i_prev
        T_step = 10
        process()
        i_curr = sq_integr()
        i_prev = i_curr
        way_counter = 0
        way = True
        while True:
            if i_curr - i_prev <= 0:
                opt_t(way, T_step)
                if T_step < 0.01:
                    break
                if i_block_regulator.Ti <= 0:
                    T_step /= 2
                    way = True
                    continue
                elif i_block_regulator.Ti >= 800:
                    T_step /= 2
                    way = False
                    continue
                process()
                i_prev = i_curr
                i_curr = sq_integr()
            else:
                way = not way
                T_step /= 2
                i_prev = i_curr
                opt_t(way, T_step)
                process()
                i_curr = sq_integr()                
                if math.fabs(i_curr - i_prev) < 0.1:
                    break
            if math.fabs(i_curr - i_prev) < 0.01 and i_curr != i_prev:
                break

    process()
    i_curr = sq_integr()
    i_prev = 0
    while math.fabs(i_curr - i_prev) > 0.1:
        optimization_k()
        optimization_T()
    print('Ti - ',  i_block_regulator.Ti)
    print('K - ',  p_block_regulator.k)
    result = {'x':[x for x in range(0, 401)],
              'y':buff}
    p_block_regulator.k = 0.2
    i_block_regulator.k = 0.2
    i_block_regulator.Ti = 100
    process()
    result['y0'] = buff
    return JsonResponse(result)
