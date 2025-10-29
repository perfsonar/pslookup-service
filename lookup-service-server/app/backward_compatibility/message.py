from .reserved_keys import ReservedKeys

class Message:

    def __init__(self, message={}):
        self.key_values = message
        self.status = 0

    def get_map(self):
        return self.key_values
    
    def get_status(self):
        return self.status
    
    def set_status(self, status):
        old = self.status
        self.status = status
        return old
    
    def has_key(self, key):
        return key in self.key_values
    
    def get_key(self, key):
        return self.key_values.get(key)
    
    def add(self, key, value):
        self.key_values[key] = value

    def get_URI(self):

        val = self.get_map().get(ReservedKeys.RECORD_URI)
        if type(val) is str:
            return val
        elif type(val) is list:
            # may error out if empty list
            return str(val[0])

        return None

    def get_TTL(self):

        val = self.get_map().get(ReservedKeys.RECORD_TTL)
        if val is not None:
            if type(val) is str:
                return val
            elif type(val) is list:
                if len(val) == 0:
                    return ""
                return str(val[0])

        return None
    
    def get_expires(self):

        val = self.get_map().get(ReservedKeys.RECORD_EXPIRES)

        if type(val) is str:
            return val
        elif type(val) is list:
            # may error out if empty list
            return str(val[0])

        return None

    def get_record_type(self):

        val = self.get_map().get(ReservedKeys.RECORD_TYPE)

        if type(val) is str:
            return val
        elif type(val) is list:
            # may error out if empty list
            return  str(val[0])
        return None

    def get_operator(self):

        val = self.get_map().get(ReservedKeys.RECORD_OPERATOR)

        if type(val) is str:
            return val
        elif type(val) is list:
            # may error out if empty list
            return  str(val[0])
        return None


    def set_error(self, error):
        self.error = error


    def validate(self):
        return_val = True

        for key in self.key_values:
            if type(self.key_values[key]) is str:
                return_val = return_val and True
            elif type(self.key_values[key]) is list:
                for element in self.key_values[key]:
                    if type(self.key_values[key]) is not str:
                        return_val = return_val and False
            else:
                return_val = False
            
        return return_val
