import json
import os
from zoneinfo import ZoneInfo
import boto3
import datetime
import logging

FORMAT = '%(asctime)s : %(message)s'
logging.basicConfig(format=FORMAT, level=logging.ERROR)

logger = logging.getLogger()
# logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

now = int(datetime.datetime.now(ZoneInfo((os.getenv('TZ', "Europe/Lisbon")))).strftime("%H"))
nowDay = datetime.datetime.today().strftime("%a").lower()

def start( schedule_dic: dict , state: str) -> str:
    businessDays = ['mon', 'tue', 'wed', 'thu', 'fri']
    weekendDays = ['sat', 'sun']    
    
    if 'business' in schedule_dic:
        schedule_detail = schedule_dic['business']
        del schedule_dic['business']
        for day_of_the_week in businessDays:
           schedule_dic[day_of_the_week] = schedule_detail 
        
    if 'weekend' in schedule_dic:
        schedule_detail = schedule_dic['weekend']
        del schedule_dic['weekend']
        for day_of_the_week in weekendDays:
           schedule_dic[day_of_the_week] = schedule_detail 
    
    if 'daily' in schedule_dic:
        schedule_detail = schedule_dic['daily']
        del schedule_dic['daily']
        for day_of_the_week in list(set(businessDays) | set(weekendDays)): 
            schedule_dic[day_of_the_week] = schedule_detail
    
    
    # Days interperter 
    if (nowDay in schedule_dic):
        actions = schedule_dic[nowDay] 
        startTime = 24
        stopTime = 24
        logger.debug(f'Schedule for today is {actions}')
        if 'stop' in actions :
            stopTime = actions['stop']
            # Decide to stop
            if startTime >= now and stopTime <= now and \
                    state == "running":
                return "stop"
            
        if 'start' in actions :    
            startTime = actions['start']
            # Decide to start

            if startTime <= now and stopTime >= now and \
                    state == "stopped":
                return "start"        

        return "no_action"
    else:
        return "no_action"


    
# EC2 handler function
def ec2_handler(session):
    startList = []
    stopList = []
    # get instances
    ec2 = session.client('ec2', region_name='eu-central-1')

    # instances = ec2.describe_instances(
    #     Filters=[{'Name': 'instance-state-name', 'Values': ['pending','running','stopping','stopped']}])

    instances = ec2.describe_instances(
        Filters=[{'Name': 'tag:schedule', 'Values': ['*']}])    
    next_token = True
    while next_token:
        for instanceReservations in instances["Reservations"]:
            for instance in instanceReservations["Instances"]:
                logger.debug(f'Evaluating EC2 instance \"{instance["InstanceId"]}\" state {instance["State"]["Name"]}')
                # match start(json.loads("{\"business\": {\"start\": [7], \"stop\": [19]}, \"weekend\": {\"start\":[8], \"stop\": [10]}}")):
                tag_dict = {tag['Key']: tag['Value'] for tag in instance["Tags"]}
                # lets see if conforms to standard
                try:
                    schedule = json.loads((tag_dict["schedule"]).lower())
                    decision = start(schedule, instance["State"]["Name"] )
                    match decision:
                        case 'start':
                            logger.debug(f'EC2 instance \"{instance["InstanceId"]}\" needs to start adding to List')
                            startList.append(instance["InstanceId"])
                        case 'stop':
                            logger.debug(f'EC2 instance \"{instance["InstanceId"]}\" needs to stop adding to List')
                            stopList.append(instance["InstanceId"])
                        case 'no_action':
                            logger.debug(f'EC2 instance \"{instance["InstanceId"]}\" has no action at this point')
                        case _ :
                            logger.error(f'Error deciding on \"{instance["InstanceId"]}\" : {decision} ')
                except Exception as e:
                    logger.error (f'Error on EC2 instance \"{instance["InstanceId"]}\" schedule \"{tag_dict["schedule"]}\": {e}')

        if 'NextToken' in instances:
            instances = ec2.describe_instances(NextToken=instances['NextToken'])
        else:
            next_token = False
    
    # Execute Start and Stop Commands
    if startList:
        logger.info(f'ACTION: Starting {len(startList)} instances:  {startList}')
        ec2.start_instances(InstanceIds=startList)
    else:
        logger.info("No Instances to Start")

    if stopList:
        logger.info(f'ACTION: Stopping {len(stopList)} instances:  {stopList}')
        ec2.stop_instances(InstanceIds=stopList)
    else:
        logger.info("No Instances to Stop")
    return f'{{"startlist" : { startList } , "stopList" : {stopList} }}'


# Main function. Entrypoint for Lambda
def handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(f'AWS_LAMBDA_LOG_GROUP_NAME={os.environ["AWS_LAMBDA_LOG_GROUP_NAME"]}')
    logger.info(f'AWS_LAMBDA_LOG_STREAM_NAME={os.environ["AWS_LAMBDA_LOG_STREAM_NAME"]}')
    logger.info('## EVENT')

    aws_session = boto3.Session()
    
    ec2_handler(aws_session)

if __name__ == "__main__":
    handler(None, None)
