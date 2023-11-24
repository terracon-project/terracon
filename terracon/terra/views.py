from django.shortcuts import render,redirect
import boto3
import botocore
from django.http import JsonResponse
import subprocess


def region(request):
    tfstr = "스트링 제대로 처리 되나요"
    return render(request,'1_1_region.html',{'tfstring' : tfstr})


def home(request):
    return render(request,'0_home.html')

def step1(request):
    return render(request,'2_step1.html')
def step2(request):
    return render(request,'3_step2.html')
aws_access_key=""
aws_secret_key=""
aws_region=""
def list(request):
    if request.method == 'POST':
        # 사용자로부터 입력 받은 AWS 액세스 키, 시크릿 키, 리전 정보
        aws_access_key = request.POST.get('aws_access_key')
        aws_secret_key = request.POST.get('aws_secret_key')
        aws_region = request.POST.get('aws_region')

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
        return render(request, '1_list.html', context)
    else:
        return render(request, '1_list.html')
def execute_selected_instances(request):
    if request.method == 'POST':
        data = request.POST
        action = data.get('action')
        instance_ids = data.getlist('instance_ids[]')  # 여러 개의 값 받기

        if action and instance_ids:
            try:
                ec2_client = boto3.client(
                    'ec2',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region
                )

                if action == 'play':
                    ec2_client.start_instances(InstanceIds=instance_ids)
                elif action == 'pause':
                    ec2_client.stop_instances(InstanceIds=instance_ids)
                elif action == 'delete':
                    ec2_client.terminate_instances(InstanceIds=instance_ids)
                # 추가적인 액션들에 대한 처리

                return JsonResponse({'message': f'인스턴스 {action} 요청이 성공했습니다.'}, status=200)
            except Exception as e:
                return JsonResponse({'message': f'오류 발생: {str(e)}'}, status=500)

        else:
            return JsonResponse({'message': '잘못된 요청입니다.'}, status=400)
    else:
        return JsonResponse({'message': '허용되지 않은 메소드입니다.'}, status=405)