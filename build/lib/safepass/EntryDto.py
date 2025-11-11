class EntryDto():
    def __init__(self, row = None):
        if row == None:
            return
        self.account_id = row['AccountId']
        self.service_name = row['ServiceName']
        self.url = row['Url']
        self.username = row['Username']
        self.password = row['Password']
        
    def __str__(self):
        result = self.service_name
        if self.url != '' and self.url != None :
            result += f' ({self.url})'
        result += '\n'
        result += f'Username: {self.username}\n' # Did not print encrypted version too because I am encrypting whole db
        result += f'Password: {self.password}'
        return result