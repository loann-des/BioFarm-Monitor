from .models import Users

nb_user : int
nb_connected_user : int

class ConnectedUser(Users) :
    cmd_history = []
    
    
    def __init__(self, user_id:int) :
        user:Users = Users.query.get(int(user_id)) # type: ignore
        self.id = user.id
        self.email = user.email
        self.password = user.password
        self.setting = user.setting
        self.medic_list = user.medic_list
        
    def get_id(self) :
        return str(self.id)
    
