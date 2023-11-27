from django.shortcuts import render,redirect
import boto3
import botocore
import subprocess
from django.http import HttpResponseRedirect
from django.http import JsonResponse
import json
# def region(request):
#     tfstr = "스트링 제대로 처리 되나요"
#     return render(request,'1_1_region.html',{'tfstring' : tfstr})

def home(request):
    return render(request,'0_home.html')

def main(request):
    if request.method == 'POST':
        # 사용자로부터 입력 받은 AWS 액세스 키, 시크릿 키, 리전 정보
        aws_access_key = request.POST.get('aws_access_key')
        aws_secret_key = request.POST.get('aws_secret_key')
        aws_region = request.POST.get('aws_region')
        request.session['aws_region'] = aws_region
        # AWS SDK를 사용하여 EC2 클라이언트 생성
        try:
            ec2_client = boto3.client(
                'ec2',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
            

            # 인스턴스 목록 가져오기
            instances = ec2_client.describe_instances()

            # 필요한 정보 추출 (인스턴스 이름, ID, 상태 등)
            instance_info_list = []
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_state = instance['State']['Name']

                    # 이름 정보 가져오기
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
                            break
                    else:
                        instance_name = 'N/A'  # 이름이 없는 경우를 대비하여 기본값 설정

                    instance_info_list.append({'id': instance_id, 'name': instance_name, 'state': instance_state})
        except:
            print('액세스 키 또는 시크릿 키가 잘못되었습니다.')
            return redirect('home')

        # HTML 템플릿에 데이터 전달
        context = {'instances_info': instance_info_list}   
        return render(request, '1_main.html', context)
    else:
        return render(request, '1_main.html')
def instances_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        instance_ids = data.get('instance_ids')
        instance_ids_str = ' '.join(instance_ids)
        # AWS 인스턴스 제어
        try:
            if action == 'start':
                    subprocess.run(f"aws ec2 start-instances --instance-ids {instance_ids_str}", shell=True)
            elif action == 'stop':
                    subprocess.run(f"aws ec2 stop-instances --instance-ids {instance_ids_str}", shell=True)
            elif action == 'terminate':
                    subprocess.run(f"aws ec2 terminate-instances --instance-ids {instance_ids_str}", shell=True)
            else:
                return JsonResponse({'message': 'Invalid action'}, status=400)

            return JsonResponse({'message': 'Success'})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request'}, status=400)

def create(request):
    aws_region = request.session.get('aws_region')
    return render(request,'2_create.html',{'aws_region':aws_region})

def view(request):
    return render(request,'3_view.html')

    #     selected_instances = request.POST.getlist('instance_ids')
    #     action = request.POST.get('action')
    #     selected_instances = json.loads(request.body)
    #     # action = selected_instances.get('action')
    #     # instance_id = selected_instances.get('instance_ids')
    #     for instance_id in selected_instances:
    #         if action == 'start':
    #             print("실행")
    #             # 인스턴스 시작
    #             subprocess.run(f"aws ec2 start-instances --instance-ids {instance_id}", shell=True)
    #         elif action == 'stop':
    #             print("정지")
    #             # 인스턴스 정지
    #             subprocess.run(f"aws ec2 stop-instances --instance-ids {instance_id}", shell=True)
    #         elif action == 'terminate':
    #             # 인스턴스 삭제
    #             subprocess.run(f"aws ec2 terminate-instances --instance-ids {instance_id}", shell=True)
        
    #     return HttpResponseRedirect('/terra/list')  # 적절한 리디렉션 URL로 변경하세요

    # return render(request, '0_home.html')    
