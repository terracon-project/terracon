import shutil
import uuid
from django.shortcuts import render,redirect
import boto3
import botocore
import subprocess
import os
from django.http import JsonResponse
import json
# def region(request):
#     tfstr = "스트링 제대로 처리 되나요"
#     return render(request,'1_1_region.html',{'tfstring' : tfstr})

def home(request):
    return render(request,'0_home.html')

def main(request):
    
    # 사용자로부터 입력 받은 AWS 액세스 키, 시크릿 키, 리전 정보
    if request.method == 'POST':
        aws_access_key = request.POST.get('aws_access_key')
        aws_secret_key = request.POST.get('aws_secret_key')
        aws_region = request.POST.get('aws_region')
        request.session['aws_region'] = aws_region
        request.session['aws_access_key'] = aws_access_key
        request.session['aws_secret_key'] = aws_secret_key
    
    # AWS SDK를 사용하여 EC2 클라이언트 생성
    try:
        ec2_client = boto3.client(
        'ec2',
            aws_access_key_id=request.session.get('aws_access_key'),
            aws_secret_access_key=request.session.get('aws_secret_key'),
            region_name=request.session.get('aws_region')
        )
        

        # 인스턴스 목록 가져오기
        instances = ec2_client.describe_instances()

        # 필요한 정보 추출 (인스턴스 이름, ID, 상태 등)
        instance_info_list = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_state = instance['State']['Name']
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
                    instance_state = '삭제 됨'                                                                                

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

            return {'message': 'Success'}

        except Exception as e:
            return {'message': str(e)}, 500
        # AWS 인스턴스 제어
        # try:
        #     if action == 'start':
        #             subprocess.run(f"aws ec2 start-instances --instance-ids {instance_ids_str}", shell=True)
        #     elif action == 'stop':
        #             subprocess.run(f"aws ec2 stop-instances --instance-ids {instance_ids_str}", shell=True)
        #     elif action == 'terminate':
        #             subprocess.run(f"aws ec2 terminate-instances --instance-ids {instance_ids_str}", shell=True)
        #     else:
        #         return JsonResponse({'message': 'Invalid action'}, status=400)

        #     return JsonResponse({'message': 'Success'})
        # except Exception as e:
        #     return JsonResponse({'message': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request'}, status=400)

def handle_terraform_request(request):
    if request.method == 'POST':
        terraform_content = request.POST.get('terraform_content')  # Assuming 'terraform_content' is the key for data sent from JavaScript
        unique_id = str(uuid.uuid4())[:8]  # 8자리의 UUID 생성
        workdir = f'terraform_workdir_{unique_id}'  # 폴더 이름에 UUID 추가
        print('hello')
        os.makedirs(workdir, exist_ok=True)
        os.chdir(workdir)

        if terraform_content:
            # Save received content to a main.tf file
            with open('main.tf', 'w') as file:
                file.write(terraform_content)

            # Execute Terraform apply using subprocess
            try: 
                with open('plan.txt', 'w') as output_file:
                    subprocess.run(['terraform', 'plan'], stdout=output_file, stderr=subprocess.STDOUT, text=True)
                # subprocess.run(['terraform', 'apply', '-auto-approve'], check=True)
                return JsonResponse({'success': True, 'message': 'Terraform plan completed successfully.'})
            except subprocess.CalledProcessError as e:
                return JsonResponse({'success': False, 'message': f'Terraform apply failed: {e}'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})
def execute_terraform(request):
    print('hello')
    if request.method == 'POST':
        print('hello')
        received_data = json.loads(request.body)
        terraform_content = received_data.get('terraform')

        unique_id = str(uuid.uuid4())[:8]  # 8자리의 UUID 생성
        workdir = f'terraform_workdir_{unique_id}'  # 폴더 이름에 UUID 추가

        os.makedirs(workdir, exist_ok=True)

        with open('main.tf', 'w') as file:
            file.write(terraform_content)
        try:
            subprocess.Popen(['terraform', 'init'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # print("test1")
            # with open('plan.txt', 'w') as output_file:
            #     subprocess.run(['terraform', 'plan'], stdout=output_file, stderr=subprocess.STDOUT, text=True)

            subprocess.Popen(['terraform', 'apply', '-auto-approve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # subprocess.run(['terraform', 'apply', '-auto-approve'], check=True)
            # subprocess.run(['terraform', 'apply', '-auto-approve'], check=True)

            # shutil.rmtree(workdir)
            return JsonResponse({'success': True, 'message': 'Terraform plan completed successfully.'})
        except subprocess.CalledProcessError as e:
            return JsonResponse({'success': False, 'message': 'Invalid request'})
        # finally:
            # shutil.rmtree(workdir, ignore_errors=True)

def create(request):
    aws_region = request.session.get('aws_region')
    return render(request,'2_create.html',{'aws_region':aws_region})

def view(request):
    return render(request,'3_view.html')

