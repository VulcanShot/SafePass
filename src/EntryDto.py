class EntryDto():
    def __init__(self, row = None):
        if row == None:
            return
        
        self.service_name = row['ServiceName']
        self.url = row['Url']
        self.username = row['Username']
        self.password = row['Password']