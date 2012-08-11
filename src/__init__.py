import json
import urllib2
from logger import initLog


API_KEY = '05743125acff7a93105c937106fe6fb9'
OPENER = urllib2.build_opener()
COUNT = 10000
API_URL='http://api.douban.com/shuo/users/%s/followers?api_key=%s&count=%s'
LOGGING=initLog()


class DBRankException(Exception):
    pass


class MasterException(DBRankException):
    pass

class UserDoesNotExistError(DBRankException):
    pass

class User(object):

    def __init__(self,level):
        self.level=level
    def get_slaves(self):
        try:
            type(self.uid)
        except AttributeError:
            raise MasterException
        else:
            users = []
            #TODO urlpattern prefered
            LOGGING.info(API_URL % (self.uid, 
                API_KEY, COUNT))
            try:
                followers = json.loads(OPENER.open(API_URL % (self.uid,
                    API_KEY,COUNT)).read())
            except urllib2.HTTPError:
                raise  UserDoesNotExistError
            for user_dict in followers:
                user=User(self.level+1)
                user.__dict__.update(user_dict)
                users.append(user)
            self.users = users
    
    def get_DBRank(self,base_level):
        if self.level == base_level:
            return 1
        try:
            self.get_slaves()
            type(self.users)
        except AttributeError:
            raise MasterException
        except UserDoesNotExistError:
            return 0
        else:
            for user in self.users:
                if user.following_count == 0:
                    continue
                DBRank =+ 0.85 * user.get_DBRank(base_level)/user.following_count
            DBRank=+0.15
            return DBRank

if __name__ == '__main__':
    user = User(0)
    user.uid = 'tonyseek'
    print  user.get_DBRank(3)
