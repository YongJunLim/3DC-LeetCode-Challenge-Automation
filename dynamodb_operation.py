import boto3
from boto3.dynamodb.conditions import Key, Attr
from mypy_boto3_dynamodb.client import CreateTableOutputTypeDef, BatchWriteItemOutputTypeDef, TableClassType
from operator import itemgetter
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from decimal import Decimal
import data_fetch

type submission_data = dict[str, dict[str, int | float | None]]

dynamodb = boto3.resource('dynamodb')

def find_table(
    table_name: str,
    table_names: list[str]
) -> bool:
    return table_name in table_names

def create_table(
    table_name: str,
    key_schema: list[dict[str, str]],
    attribute_def: list[dict[str, str]]
) -> CreateTableOutputTypeDef:
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_def,
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    table.wait_until_exists()
    
    return table

def find_users_to_update(
    user_list: tuple[str],
    table_obj: TableClassType
) -> tuple[str]:
    current_datetime = datetime.now(ZoneInfo('Asia/Singapore')).strftime('%Y%m%d%H%M')
    response = table_obj.scan(
        FilterExpression=Attr('lastUpdated').gte(int(current_datetime)),
        Select='SPECIFIC_ATTRIBUTES',
        ProjectionExpression='username'
    )
    existing_updated_users = tuple(map(itemgetter('username'), response['Items']))
    print(existing_updated_users)
    users_to_add = tuple(filter(
        lambda user: user not in existing_updated_users,
        user_list
    ))
    print(users_to_add)
    return users_to_add

def batch_write_users(
    user_list: tuple[str],
    table_obj: TableClassType
) -> None:
    with table_obj.batch_writer() as users_batch:
        for user in user_list:
            users_batch.put_item(Item=user)

def update_progress(
    user_progress_list: dict[str, str | int| submission_data],
    table_obj: TableClassType
) -> None:
    with table_obj.batch_writer() as progress_batch:
        for progress in user_progress_list:
            # print(progress)
            for difficulty_percentile in ('easy_percentile', 'medium_percentile', 'hard_percentile'):
                percentile = progress[difficulty_percentile]
                if percentile:
                    progress[difficulty_percentile] = Decimal(str(percentile))
                else:
                    progress[difficulty_percentile] = Decimal('0')
            progress_item = {
                'username': progress['username'],
                'easy': progress['easy'],
                'medium': progress['medium'],
                'hard': progress['hard'],
                'easy_percentile': progress['easy_percentile'],
                'medium_percentile': progress['medium_percentile'],
                'hard_percentile': progress['hard_percentile'],
                'lastUpdated': progress['lastUpdated']
            }
            progress_batch.put_item(Item=progress_item)

def get_month_earliest_progress(
    table_obj: TableClassType
) -> list[dict[submission_data]]:
    current_datetime_obj = datetime.now(ZoneInfo('Asia/Singapore'))
    current_datetime = int(current_datetime_obj.strftime('%Y%m%d%H%M'))
    max_datetime = int(get_last_day_of_month(current_datetime_obj).strftime('%Y%m%d%H%M'))
    min_datetime = int(get_first_day_of_month(current_datetime_obj).strftime('%Y%m%d%H%M'))

    response = table_obj.scan(
        FilterExpression=Key('lastUpdated').between(min_datetime, max_datetime)
    )

    # earliest data about progress in current month
    earliest_month_progress = {}
    for progress in response['Items']:
        username = progress['username']
        if username not in earliest_month_progress or progress['lastUpdated'] < earliest_month_progress[username]['lastUpdated']:
            earliest_month_progress[username] = progress

    return earliest_month_progress

def get_last_day_of_month(datetime_obj):
    next_month = datetime_obj.replace(
        day=28,hour=23,
        minute=59,second=59,
        microsecond=999999
    ) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)

def get_first_day_of_month(datetime_obj):
    return datetime_obj.replace(
        day=1,hour=0,
        minute=0,second=0,
        microsecond=0
    )

# progress_table = dynamodb.Table('3DC_LeetCode_Progress') # DYNAMODB_3DC_PROGRESS_TABLE)

# print(get_month_earliest_progress(progress_table))