import requests
from zoneinfo import ZoneInfo
from datetime import datetime
from constants import LEETCODE_GRAPHQL_ENDPOINT, LEETCODE_USER_PROFILE_QUERY, LEETCODE_QUESTION_PROGRESS_QUERY, LEETCODE_SESSION_PROGRESS_QUERY

# type leetcode_graphql_query = dict[str, str | dict[str, str]]
type submission_data = dict[str, dict[str, int | float | None]]
type user_progress_data = dict[str, str | int | submission_data | None]

def get_user_leetcode_info(
    username: str, 
    # user_profile_query: leetcode_graphql_query, 
    # question_progress_query: leetcode_graphql_query, 
    # session_progress_query: leetcode_graphql_query, 
    user_progress: user_progress_data
) -> user_progress_data | None:

    user_profile_query = LEETCODE_USER_PROFILE_QUERY.copy()
    question_progress_query = LEETCODE_QUESTION_PROGRESS_QUERY.copy()
    session_progress_query = LEETCODE_SESSION_PROGRESS_QUERY.copy()

    user_profile_query["variables"]["username"] = username
    question_progress_query["variables"]["userSlug"] = username
    session_progress_query["variables"]["username"] = username

    user_profile_response = requests.post(LEETCODE_GRAPHQL_ENDPOINT, json=user_profile_query)
    if not user_profile_response.json()['data']['matchedUser']:
        return None
    user_school = user_profile_response.json()['data']['matchedUser']['profile']['school']
    if user_school != 'SUTD':
        return None

    current_datetime = datetime.now(ZoneInfo('Asia/Singapore')).strftime('%Y%m%d%H%M')

    user_progress['username'] = user_profile_response.json()['data']['matchedUser']['username']
    user_progress['ranking'] = user_profile_response.json()['data']['matchedUser']['profile']['ranking']
    user_progress['realName'] = user_profile_response.json()['data']['matchedUser']['profile']['realName']
    user_progress['school'] = user_school
    user_progress['lastUpdated'] = int(current_datetime)

    question_progress_response = requests.post(LEETCODE_GRAPHQL_ENDPOINT, json=question_progress_query)
    session_progress_response = requests.post(LEETCODE_GRAPHQL_ENDPOINT, json=session_progress_query)
    percentile_submission_counts = question_progress_response.json()['data']['userProfileUserQuestionProgressV2']['userSessionBeatsPercentage']
    accepted_submission_counts = session_progress_response.json()['data']['matchedUser']['submitStats']['acSubmissionNum']
    total_submission_counts = session_progress_response.json()['data']['matchedUser']['submitStats']['acSubmissionNum']

    for percentile_submission_count in percentile_submission_counts:
        difficulty = percentile_submission_count['difficulty'].lower()
        user_progress['submissions'][difficulty]['percentile'] = percentile_submission_count['percentage']
    for accepted_submission_count in accepted_submission_counts:
        difficulty = accepted_submission_count['difficulty'].lower()
        user_progress['submissions'][difficulty]['accepted'] = accepted_submission_count['count']
    for total_submission_count in total_submission_counts:
        difficulty = total_submission_count['difficulty'].lower()
        user_progress['submissions'][difficulty]['total'] = total_submission_count['submissions']

    return user_progress