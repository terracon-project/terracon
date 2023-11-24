from django.shortcuts import render,redirect
import boto3
def region(request):
    tfstr = "스트링 제대로 처리 되나요"
    return render(request,'1_1_region.html',{'tfstring' : tfstr})


def home(request):
    return render(request,'0_home.html')

def step1(request):
    return render(request,'2_step1.html')
def step2(request):
    return render(request,'3_step2.html')

def list(request):
    if request.method == 'POST':
        # 사용자로부터 입력 받은 AWS 액세스 키, 시크릿 키, 리전 정보
        aws_access_key = request.POST.get('aws_access_key')
        aws_secret_key = request.POST.get('aws_secret_key')
        aws_region = request.POST.get('aws_region')

        # AWS SDK를 사용하여 EC2 클라이언트 생성
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

        # HTML 템플릿에 데이터 전달
        context = {'instances_info': instance_info_list}
        return render(request, '1_list.html', context)
    else:
        return render(request, '0_home.html')
   