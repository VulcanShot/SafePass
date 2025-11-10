CREATE_TABLES = """\
CREATE TABLE IF NOT EXISTS Service (
    ServiceId integer,
    Name text unique not null collate nocase,
    Url text collate nocase,
    PRIMARY KEY (ServiceId)
);
    
CREATE TABLE IF NOT EXISTS Account (
    AccountId integer,
    ServiceId integer,
    Username text,
    Password text,
    PRIMARY KEY (AccountId),
    FOREIGN KEY (ServiceId) REFERENCES Service (ServiceId)
);
"""

SELECT_ENTRY = """\
SELECT s.Name as ServiceName, s.Url, a.AccountId, a.Username, a.Password
FROM Service s
INNER JOIN Account a ON s.ServiceId = a.ServiceId
WHERE s.Name = ?
OR s.Url = ?
"""

SELECT_SERVICE = """\
SELECT 1
FROM Service
WHERE Name = ?    
"""

SELECT_ALL = """\
SELECT s.Name as ServiceName, s.Url, a.AccountId, a.Username, a.Password
FROM Service s
INNER JOIN Account a ON s.ServiceId = a.ServiceId
"""

INSERT_SERVICE = """\
INSERT INTO Service(Name, Url) VALUES (?, ?)
"""

INSERT_ACCOUNT = """\
INSERT INTO Account(ServiceId, Username, Password) VALUES (
    (SELECT ServiceId
    FROM Service
    WHERE Name = ?),
    ?,
    ?
)
"""

DELETE_ACCOUNT = """\
DELETE FROM Account
WHERE AccountId = ?
"""