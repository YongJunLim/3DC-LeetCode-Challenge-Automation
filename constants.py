import os
from dotenv import dotenv_values

USER_PROGRESS_DATA = {
    'username': None,
    'ranking': None, 
    'realName': None, 
    'school': None,
    'lastUpdated': None,
    'submissions': {
        'all': {
            'accepted': None,
            'total': None
        },
        'easy': {
            'accepted': None,
            'total': None,
            'percentile': None
        },
        'medium': {
            'accepted': None,
            'total': None,
            'percentile': None
        },
        'hard': {
            'accepted': None,
            'total': None,
            'percentile': None
        }
    }
}
LEETCODE_GRAPHQL_ENDPOINT = "https://leetcode.com/graphql/"
LEETCODE_USER_PROFILE_QUERY = {
    "query": """
    query userPublicProfile($username: String!) {
        matchedUser(username: $username) {
            username
            profile {
            ranking
            realName
            school
            }
        }
    }
    """,
    "variables": {
        "username": None
    },
    "operationName": "userPublicProfile"
}
LEETCODE_QUESTION_PROGRESS_QUERY = {
    "query": """
    query userProfileUserQuestionProgressV2($userSlug: String!) {
        userProfileUserQuestionProgressV2(userSlug: $userSlug) {
            numAcceptedQuestions {
                count
                difficulty
            }
            userSessionBeatsPercentage {
                difficulty
                percentage
            }
        }
    }
    """,
    "variables": {
        "userSlug": None
    },
    "operationName": "userProfileUserQuestionProgressV2"
}
LEETCODE_SESSION_PROGRESS_QUERY = {
    "query": """
    query userSessionProgress($username: String!) {
        matchedUser(username: $username) {
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                    submissions
                }
            }
        }
    }
    """,
    "variables": {
        "username": None
    },
    "operationName": "userSessionProgress"
}
TELEGRAM_DETAILS = {
    'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
    'MAIN_3DC_CHAT_ID': os.getenv('MAIN_3DC_CHAT_ID'),
    'MAIN_3DC_CHAT_TITLE': os.getenv('MAIN_3DC_CHAT_TITLE'),
    'MAIN_3DC_TOPIC_THREAD_ID': os.getenv('MAIN_3DC_TOPIC_THREAD_ID'),
    'MAIN_3DC_TOPIC_THREAD_NAME': os.getenv('MAIN_3DC_TOPIC_THREAD_NAME'),
    'EXCO_3DC_CHAT_ID': os.getenv('EXCO_3DC_CHAT_ID'),
    'EXCO_3DC_TOPIC_THREAD_ID': os.getenv('EXCO_3DC_TOPIC_THREAD_ID'),
    'EXCO_3DC_TOPIC_THREAD_NAME': os.getenv('EXCO_3DC_TOPIC_THREAD_NAME'),
    'EXCO_3DC_CHAT_TITLE': os.getenv('EXCO_3DC_CHAT_TITLE'),
    'DYNAMODB_3DC_USERS_TABLE': os.getenv('DYNAMODB_3DC_USERS_TABLE'),
    'DYNAMODB_3DC_PROGRESS_TABLE': os.getenv('DYNAMODB_3DC_PROGRESS_TABLE'),
    'ALLOWED_USER_IDS': list(map(int, os.getenv('ALLOWED_USER_IDS').split(",")))
}
SCORE_MULTIPLER = {
    'easy': 1,
    'medium': 3,
    'hard': 6
}
DYNAMODB_3DC_USERS_TABLE_KEY_SCHEMA = [
    {
        'AttributeName': 'username',
        'KeyType': 'HASH'
    },
    {
        'AttributeName': 'ranking',
        'KeyType': 'RANGE'
    }
]
DYNAMODB_3DC_USERS_TABLE_KEY_ATTRIBUTE_DEF = [
    {
        'AttributeName': 'username',
        'AttributeType': 'S'
    },
    {
        'AttributeName': 'ranking',
        'AttributeType': 'N'
    }
]
DYNAMODB_3DC_PROGRESS_TABLE_KEY_SCHEMA = [
    {
        'AttributeName': 'username',
        'KeyType': 'HASH'
    },
    {
        'AttributeName': 'lastUpdated',
        'KeyType': 'RANGE'
    }
]
DYNAMODB_3DC_PROGRESS_TABLE_KEY_ATTRIBUTE_DEF = [
    {
        'AttributeName': 'username',
        'AttributeType': 'S'
    },
    {
        'AttributeName': 'lastUpdated',
        'AttributeType': 'N'
    }
]