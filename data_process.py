from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from operator import itemgetter
from constants import SCORE_MULTIPLER

type submission_data = dict[str, dict[str, int | float | None]]
type user_progress_data = dict[str, str | int]

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

def rank_users(
    earliest_progress_list,
    user_progress_list
) -> list[str, int]:
    user_scores = {}
    for progress in user_progress_list:
        current_score = SCORE_MULTIPLER['easy'] * int(progress['easy']) + SCORE_MULTIPLER['medium'] * int(progress['medium']) + SCORE_MULTIPLER['hard'] * int(progress['hard'])
        user_scores[progress['username']] = current_score
    for progress in earliest_progress_list.values():
        initial_score = SCORE_MULTIPLER['easy'] * int(progress['easy']) + SCORE_MULTIPLER['medium'] * int(progress['medium']) + SCORE_MULTIPLER['hard'] * int(progress['hard'])
        user_scores[progress['username']] = (user_scores[progress['username']] - initial_score)
    return sorted(user_scores.items(),key=lambda item: item[1], reverse=True)

def generate_leaderboard(ranked_users: list[str, int], leaderboard_type: str) -> str:
    current_datetime = datetime.now(ZoneInfo('Asia/Singapore'))
    current_month = current_datetime.strftime('%B')
    current_day = current_datetime.day
    output = ""
    for rank, user_progress in enumerate(ranked_users):
        output += f"{rank+1:<4}{user_progress[0]:20}{user_progress[1]}\n"
    match leaderboard_type:
        case 'FINALISED':
            # in case AWS does not run it on time
            current_month = (current_datetime - timedelta(hours=5)).strftime('%B')
            output = f"🔥 *Final LeetCode Leaderboard for {current_month}* 🔥\n`\n{output}`"
        case 'CURRENT':
            output = f"🔥 *Current LeetCode Leaderboard for {current_month}* 🔥\n`\n{output}`"

    return output