from django.shortcuts import render,redirect

def main(request):
    return render(request,'0_main.html')
def region(request):
    tfstr = "스트링 제대로 처리 되나요"
    return render(request,'1_1_region.html',{'tfstring' : tfstr})
def instance(request):
    return render(request,'1_2_ins_type.html')
def key(request):
    return render(request,'1_3_key.html')


def home(request):
    return render(request,'0_home.html')
def list(request):
    tfstr = "스트링 제대로 처리 되나요"
    return render(request,'1_list.html',{'tfstring' : tfstr})
def step1(request):
    return render(request,'2_step1.html')
def step2(request):
    return render(request,'3_step2.html')
