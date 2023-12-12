import shutil
import time
import uuid
from django.shortcuts import render,redirect
import boto3
import botocore
import subprocess
import os
from django.http import JsonResponse
import json

def home(request):
    return render(request,'0_home.html')
def key_login(aws_access_key, aws_secret_key, aws_region):

    command = f'aws configure set aws_access_key_id {aws_access_key} && ' \
              f'aws configure set aws_secret_access_key {aws_secret_key} && ' \
              f'aws configure set region {aws_region} && ' \
              f'aws configure set output json'
    subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
def main(request):
    # 사용자로부터 입력 받은 AWS 액세스 키, 시크릿 키, 리전 정보
    if request.method == 'POST':
        
        aws_access_key = request.POST.get('aws_access_key')
        aws_secret_key = request.POST.get('aws_secret_key')
        aws_region = request.POST.get('aws_region')
        request.session['aws_region'] = aws_region
        request.session['aws_access_key'] = aws_access_key
        request.session['aws_secret_key'] = aws_secret_key
        #key_login(request.session.get('aws_access_key'),request.session.get('aws_secret_key'),request.session.get('aws_region'))
    # AWS SDK를 사용하여 EC2 클라이언트 생성
    try:
        print(request.session.get('aws_access_key'),)
        ec2_client = boto3.client(
        'ec2',
            aws_access_key_id=request.session.get('aws_access_key'),
            aws_secret_access_key=request.session.get('aws_secret_key'),
            region_name=request.session.get('aws_region')
        )

    # AWS CLI의 aws configure 명령을 실행

        # 인스턴스 목록 가져오기
        instances = ec2_client.describe_instances()
    except:
        print('액세스 키 또는 시크릿 키가 잘못되었습니다.')
        return redirect('home')
        # 필요한 정보 추출 (인스턴스 이름, ID, 상태 등)
    instance_info_list = []
    for reservation in instances['Reservations']:                     
        for instance in reservation['Instances']:
            try:
                if(instance['PublicDnsName']==''):
                    instance_public_dns='-'
                else:
                    instance_public_dns = instance['PublicDnsName']
        
                try:
                    instance_public_ip = instance['PublicIpAddress']
                except:
                    instance_public_ip='-'
                
                if(instance['State']['Name'] =='running'):
                    instance_state = '실행 중'
                if(instance['State']['Name'] =='pending'):
                    instance_state = '준비 중'
                if(instance['State']['Name'] =='stopping'):
                    instance_state = '중지 중'
                if(instance['State']['Name'] =='stopped'):
                    instance_state = '중지 됨'
                if(instance['State']['Name'] =='shutting-down'):
                    instance_state = '삭제 중'
                if(instance['State']['Name'] =='terminated'):
                    continue                              
                # 이름 정보 가져오기
                instance_id = instance['InstanceId']

                instance_time = instance['LaunchTime']
                instance_ami = instance['ImageId']
                instance_type = instance['InstanceType']
                instance_private_dns = instance['PrivateDnsName']
                instance_private_ip = instance['PrivateIpAddress']
                instance_subnet = instance['SubnetId']
                instance_vpc = instance['VpcId']

                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                        break
                else:
                    instance_name = '-'  # 이름이 없는 경우를 대비하여 기본값 설정

                instance_info_list.append({'id': instance_id, 'name': instance_name, 'public_ip':instance_public_ip, 'state': instance_state, 'time': str(instance_time), 'ami': instance_ami, 'type': instance_type, 'public_dns': instance_public_dns, 'private_dns': instance_private_dns, 'private_ip': instance_private_ip, 'subnet': instance_subnet, 'vpc': instance_vpc});
            except:
                continue
    # HTML 템플릿에 데이터 전달
    context = {'instances_info': instance_info_list}   
    return render(request, '1_main.html', context)

         
def instances_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        instance_ids = data.get('instance_ids')
        #instance_ids_str = ' '.join(instance_ids)
        session = boto3.Session(
                aws_access_key_id=request.session.get('aws_access_key'),
                aws_secret_access_key=request.session.get('aws_secret_key'),
                region_name=request.session.get('aws_region')
            )
        ec2 = session.client('ec2')

        try:
            if action == 'start':
                ec2.start_instances(InstanceIds=instance_ids)
            elif action == 'stop':
                ec2.stop_instances(InstanceIds=instance_ids)
            elif action == 'terminate':
                ec2.terminate_instances(InstanceIds=instance_ids)
            else:
                return {'message': 'Invalid action'}, 400
            return JsonResponse({'message': 'Success'})

        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    
    return JsonResponse({'message': 'Invalid request'}, status=400)

def execute_terraform(request):
    if request.method == 'POST':
        received_data = json.loads(request.body)
        terraform_content = received_data.get('terraform')
        unique_id = str(uuid.uuid4())[:8]  # 8자리의 UUID 생성
        workdir = f'terraform_workdir_{unique_id}'  # 폴더 이름에 UUID 추가
        key_login(request.session.get('aws_access_key'),request.session.get('aws_secret_key'),request.session.get('aws_region'))
        os.makedirs(workdir, exist_ok=True)
        # main.tf 파일 생성
        with open(os.path.join(workdir, 'main.tf'), 'w') as file:
            file.write(terraform_content)
        try:
            subprocess.run(['terraform', 'init'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workdir)
            subprocess.run(['terraform', 'apply', '-auto-approve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workdir, check=True)
            time.sleep(1)
            # proc = subprocess.Popen(['terraform', 'init'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workdir)
            # stdout, stderr = proc.communicate()
            # process = subprocess.Popen(['terraform', 'apply', '-auto-approve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workdir)
            # subprocess.run(['terraform', 'init'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workdir)
            # process = subprocess.Popen(['terraform', 'apply', '-auto-approve', '-parallelism=10'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workdir)
        except subprocess.CalledProcessError as e:
            return JsonResponse({'success': False, 'message': 'Invalid request'})
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
    return JsonResponse({'success': True, 'message': 'Terraform apply completed successfully.'})

def create(request):
    aws_region = request.session.get('aws_region')
    return render(request,'2_create.html',{'aws_region':aws_region})

def view(request):
    return render(request,'3_view.html')

