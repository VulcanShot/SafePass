CREATE_TABLES = """\
CREATE TABLE IF NOT EXISTS Service (
    ServiceId integer,
    Name text unique not null collate nocase,
    Url text unique collate nocase,
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
SELECT s.Name as ServiceName, s.Url, a.Username, a.Password
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

INSERT_SERVICE = """\
INSERT INTO Service(Name, Url) VALUES (?, ?)
"""

INSERT_ENTRY = """\
INSERT INTO Account(ServiceId, Username, Password) VALUES (
    (SELECT ServiceId
    FROM Service
    WHERE Name = ?),
    ?,
    ?
)
"""

DELETE_ENTRY = """\
DELETE FROM Account
WHERE AccountId = (
    SELECT a.AccountId
    FROM Service s
    INNER JOIN Account a ON s.ServiceId = a.ServiceId
    WHERE s.Name = ?
    OR s.Url = ?
    LIMIT 1
)
"""