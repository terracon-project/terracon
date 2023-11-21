from django.shortcuts import render,redirect

def main(request):
    return render(request,'0_main.html')
def region(request):
    return render(request,'1_1_region.html')
def instance(request):
    return render(request,'1_2_ins_type.html')

