


class User(object):
    def __init__(self,user_data):
        name=user_data['author']
        home_link=user_data['author_home']
        follower_count=user_data['follower_count']
