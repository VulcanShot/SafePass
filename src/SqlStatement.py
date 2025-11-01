class SqlStatement():
    CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS Service (
    ServiceId int,
    Name text unique not null,
    Domain text unique,
    PRIMARY KEY (ServiceId)
);
    
CREATE TABLE IF NOT EXISTS Account (
    AccountId int,
    ServiceId int,
    Username text,
    Password text,
    PRIMARY KEY (AccountId),
    FOREIGN KEY (ServiceId) REFERENCES Service (ServiceId)
);
"""