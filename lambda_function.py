import os
import json
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import boto3
import data_fetch
import data_process
import dynamodb_operation
from constants import USER_PROGRESS_DATA, TELEGRAM_DETAILS, DYNAMODB_3DC_USERS_TABLE_KEY_SCHEMA, DYNAMODB_3DC_USERS_TABLE_KEY_ATTRIBUTE_DEF, DYNAMODB_3DC_PROGRESS_TABLE_KEY_SCHEMA, DYNAMODB_3DC_PROGRESS_TABLE_KEY_ATTRIBUTE_DEF

TELEGRAM_BOT_TOKEN = TELEGRAM_DETAILS['TELEGRAM_BOT_TOKEN']
MAIN_3DC_CHAT_ID = TELEGRAM_DETAILS['MAIN_3DC_CHAT_ID']
MAIN_3DC_CHAT_TITLE = TELEGRAM_DETAILS['MAIN_3DC_CHAT_TITLE']
MAIN_3DC_TOPIC_THREAD_ID = TELEGRAM_DETAILS['MAIN_3DC_TOPIC_THREAD_ID']
MAIN_3DC_TOPIC_THREAD_NAME = TELEGRAM_DETAILS['MAIN_3DC_TOPIC_THREAD_NAME']
EXCO_3DC_CHAT_ID = TELEGRAM_DETAILS['EXCO_3DC_CHAT_ID']
EXCO_3DC_TOPIC_THREAD_ID = TELEGRAM_DETAILS['EXCO_3DC_TOPIC_THREAD_ID']
EXCO_3DC_TOPIC_THREAD_NAME = TELEGRAM_DETAILS['EXCO_3DC_TOPIC_THREAD_NAME']
EXCO_3DC_CHAT_TITLE = TELEGRAM_DETAILS['EXCO_3DC_CHAT_TITLE']
DYNAMODB_3DC_USERS_TABLE = TELEGRAM_DETAILS['DYNAMODB_3DC_USERS_TABLE']
DYNAMODB_3DC_PROGRESS_TABLE = TELEGRAM_DETAILS['DYNAMODB_3DC_PROGRESS_TABLE']
ALLOWED_USER_IDS = TELEGRAM_DETAILS['ALLOWED_USER_IDS']

type LAMBDA_EVENT = dict[str, str]

application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
async def generate_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate LeetCode leaderboard."""
    leaderboard_type = context.args[0]
    users = # redacted
    user_progress_list = []
    user_list = []

    dynamodb = boto3.resource('dynamodb')
    client = boto3.client('dynamodb')

    response = client.list_tables()
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        table_names = response['TableNames']
    if not dynamodb_operation.find_table(DYNAMODB_3DC_USERS_TABLE, table_names):
        print(dynamodb_operation.create_table(
            DYNAMODB_3DC_USERS_TABLE,
            DYNAMODB_3DC_USERS_TABLE_KEY_SCHEMA,
            DYNAMODB_3DC_USERS_TABLE_KEY_ATTRIBUTE_DEF
        ))
    users_table = dynamodb.Table(DYNAMODB_3DC_USERS_TABLE)
    users_to_add = dynamodb_operation.find_users_to_update(users, users_table)
    total_users_to_query = len(users_to_add)
    for count, user in enumerate(users_to_add):
        # reset user_progress for every queried user
        user_progress = USER_PROGRESS_DATA.copy()
        user_progress = data_fetch.get_user_leetcode_info(
            user,
            user_progress
        )
        if count == 0:
            await context.bot.send_message(
                chat_id=EXCO_3DC_CHAT_ID,
                message_thread_id=EXCO_3DC_TOPIC_THREAD_ID,
                text=f"Querying {total_users_to_query} users for LeetCode leaderboard"
            )
        elif count % 15 == 0:
            await context.bot.send_message(
                chat_id=EXCO_3DC_CHAT_ID,
                message_thread_id=EXCO_3DC_TOPIC_THREAD_ID,
                text=f"Queried {count} out of {total_users_to_query} users"
            )
        elif count == total_users_to_query:
            await context.bot.send_message(
                chat_id=EXCO_3DC_CHAT_ID,
                message_thread_id=EXCO_3DC_TOPIC_THREAD_ID,
                text=f"Finished querying {total_users_to_query} users"
            )
        if user_progress:
            user_progress_list.append(
                {
                    'username': user_progress['username'],
                    'easy': user_progress['submissions']['easy']['accepted'],
                    'medium': user_progress['submissions']['medium']['accepted'],
                    'hard': user_progress['submissions']['hard']['accepted'],
                    'easy_percentile': user_progress['submissions']['easy']['percentile'],
                    'medium_percentile': user_progress['submissions']['medium']['percentile'],
                    'hard_percentile': user_progress['submissions']['hard']['percentile'],
                    'lastUpdated': user_progress['lastUpdated']
                }
            )
            user_list.append(
                {
                    'username': user_progress['username'],
                    'lastUpdated': user_progress['lastUpdated'],
                    'ranking': user_progress['ranking'],
                    'realName': user_progress['realName'],
                    'school': user_progress['school']
                }
            )
    dynamodb_operation.batch_write_users(user_list, users_table)

    if not dynamodb_operation.find_table(DYNAMODB_3DC_PROGRESS_TABLE, table_names):
        print(dynamodb_operation.create_table(
            DYNAMODB_3DC_PROGRESS_TABLE,
            DYNAMODB_3DC_PROGRESS_TABLE_KEY_SCHEMA,
            DYNAMODB_3DC_PROGRESS_TABLE_KEY_ATTRIBUTE_DEF
        ))
    progress_table = dynamodb.Table(DYNAMODB_3DC_PROGRESS_TABLE)
    dynamodb_operation.update_progress(user_progress_list, progress_table)

    earliest_progress_list = dynamodb_operation.get_month_earliest_progress(progress_table)
    ranked_users = data_process.rank_users(earliest_progress_list, user_progress_list)
    
    leaderboard_output = data_process.generate_leaderboard(ranked_users, leaderboard_type)

    await context.bot.send_message(
        chat_id=MAIN_3DC_CHAT_ID, 
        message_thread_id=MAIN_3DC_TOPIC_THREAD_ID,
        parse_mode='MarkdownV2',
        text=leaderboard_output
    )

    await context.bot.send_message(
        chat_id=EXCO_3DC_CHAT_ID,
        message_thread_id=EXCO_3DC_TOPIC_THREAD_ID,
        text=f'Sent leaderboard to the "{MAIN_3DC_CHAT_TITLE}" group under "{MAIN_3DC_TOPIC_THREAD_NAME}"!'
    )

def lambda_handler(event: LAMBDA_EVENT, context: ContextTypes.DEFAULT_TYPE) -> asyncio.Future:
    return asyncio.get_event_loop().run_until_complete(main(event, context))

async def main(event, context) -> dict[str, str | int]:
    generate_leaderboard_handler = CommandHandler(
        'generateLeaderboard', 
        generate_leaderboard,
        filters.User(user_id=ALLOWED_USER_IDS)
    )
    application.add_handler(generate_leaderboard_handler)
    
    try:    
        await application.initialize()
        event = {
            "body": "{\"update_id\":967060556,\"message\":{\"message_id\":826,\"from\":{\"id\":685660590,\"is_bot\":false,\"first_name\":\"Yong Jun\",\"username\":\"limyongjun\",\"language_code\":\"en\"},\"chat\":{\"id\":-1002094480173,\"title\":\"3DC EXCO Y24/25\",\"is_forum\":true,\"type\":\"supergroup\"},\"date\":1717864659,\"message_thread_id\":546,\"reply_to_message\":{\"message_id\":546,\"from\":{\"id\":685660590,\"is_bot\":false,\"first_name\":\"Yong Jun\",\"username\":\"limyongjun\",\"language_code\":\"en\"},\"chat\":{\"id\":-1002094480173,\"title\":\"3DC EXCO Y24/25\",\"is_forum\":true,\"type\":\"supergroup\"},\"date\":1717521029,\"message_thread_id\":546,\"forum_topic_created\":{\"name\":\"LEETCODE TESTING\",\"icon_color\":7322096},\"is_topic_message\":true},\"text\":\"/generateLeaderboard CURRENT\",\"entities\":[{\"offset\":0,\"length\":20,\"type\":\"bot_command\"}],\"is_topic_message\":true}}"
        }
        await application.process_update(
            Update.de_json(json.loads(event["body"]), application.bot)
        )
    
        return {
            'statusCode': 200,
            'body': 'Success'
        }

    except Exception as exc:
        return {
            'statusCode': 500,
            'body': 'Failure'
        }