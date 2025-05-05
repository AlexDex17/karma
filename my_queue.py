from collections import deque

queue = deque()       # очередь пользователей
videos = {}           # временно храним кружки

def add_to_queue(user_id, file_id):
    videos[user_id] = file_id
    queue.append(user_id)

def get_next_in_queue(current_user):
    while len(queue) > 0:
        user = queue.popleft()
        if user != current_user:
            return user
    return None

def get_video_by_user(user_id):
    return videos.get(user_id)