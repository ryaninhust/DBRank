import json
import urllib2
from logger import initLog


API_KEY = '05743125acff7a93105c937106fe6fb9'
OPENER = urllib2.build_opener()
COUNT = 10000
API_URL='http://api.douban.com/shuo/users/%s/followers?api_key=%s&count=%s'
LOGGING=initLog()
MEMCACHE={}


class DBRankException(Exception):
    pass


class MasterException(DBRankException):
    pass

class UserDoesNotExistError(DBRankException):
    pass


class ConnectError(DBRankException):
    pass


def memcache(function):
    def _wrap(*args,**kwargs):
        print args
        return function(*args,**kwargs)
    return _wrap


    
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
            except urllib2.URLError:
                raise  ConnectError
            for user_dict in followers:
                user=User(self.level+1)
                user.__dict__.update(user_dict)
                users.append(user)
            self.users = users
    

    def check_memcache(self):
        DBRank=MEMCACHE.get(self.uid,None)
        return DBRank

    def conditional_cache(self):
        DBRank = MEMCACHE.get(self.uid,None)
        if DBRank and DBRank[0] < self.level:
            return DBRank[1]
        else:
            return None
            
    def get_DBRank(self,base_level):
        DBRank = self.conditional_cache()
        if DBRank:
            LOGGING.info('MEMCACHE HIT!')
            return DBRank
        if self.level == base_level:
           # MEMCACHE[self.uid]=1.00000
            return 1.00000
        try:
            self.get_slaves()
            type(self.users)
        except AttributeError:
            raise MasterException
        except (UserDoesNotExistError, ConnectError):
            return 0.00000
        else:
            DBRank = 0.00000
            for user in self.users:
                if user.following_count == 0:
                    continue
                DBRank = DBRank + 0.85000 * user.get_DBRank(base_level)/user.following_count
            DBRank =DBRank + 0.15000
            MEMCACHE[self.uid] = (self.level, DBRank)
            return DBRank

if __name__ == '__main__':
    user = User(0)
    user.uid = 'ryancoder'
    user.get_slaves()
    user.get_DBRank(2)
    for _user in user.users:
        print ('%s:%f') % (_user.screen_name, MEMCACHE[_user.uid][1])

        

