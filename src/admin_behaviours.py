from introspect import Associate
import random

@Associate("color_change")
def setRandomColor(ctrl,ctx):
    for i in range(len(ctx.baseColor)):
        ctx.baseColor[i] = ctx.baseColor[i]+ random.randint(30,220)

@Associate("50cc")
def setThrottleEasy(ctrl,ctx):
    ctx.throttle_ctrl.configureBaseThrottle(0.02)

@Associate("100cc")
def setThrottleEasy(ctrl, ctx):
    ctx.throttle_ctrl.configureBaseThrottle(0.30)

@Associate("150cc")
def setThrottleEasy(ctrl, ctx):
    ctx.throttle_ctrl.configureBaseThrottle(0.80)
