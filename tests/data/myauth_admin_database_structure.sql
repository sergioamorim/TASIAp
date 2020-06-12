DROP TABLE IF EXISTS login;
CREATE TABLE login (id INTEGER(11) PRIMARY KEY AUTO_INCREMENT,
                    cliente_id INT(11) NOT NULL DEFAULT 0,
                    user VARCHAR(80) NOT NULL,
                    pass VARCHAR(50) NOT NULL,
                    ip VARCHAR(15) NOT NULL,
                    mac VARCHAR(17) NOT NULL,
                    groupname VARCHAR(80) NOT NULL,
                    enable TINYINT(4) NOT NULL DEFAULT 1,
                    proxy VARCHAR(6) NOT NULL,
                    radsyncframedip TINYINT(1) NOT NULL DEFAULT 0,
                    radsyncmac TINYINT(1) NOT NULL DEFAULT 0,
                    radsyncsim TINYINT(1) NOT NULL DEFAULT 0,
                    radsyncmkurl TINYINT(1) NOT NULL DEFAULT 0,
                    radnas_id INTEGER(11) NOT NULL DEFAULT 0,
                    accesspoint INTEGER(11) NOT NULL DEFAULT 0,
                    info TEXT DEFAULT NULL) DEFAULT CHARACTER SET latin1;

DROP TABLE IF EXISTS login_radius;
CREATE TABLE login_radius (id INTEGER(11) PRIMARY KEY AUTO_INCREMENT,
                           type ENUM('C', 'R') NOT NULL DEFAULT 'R',
                           user VARCHAR(80) NOT NULL,
                           attribute VARCHAR(40) NOT NULL,
                           op VARCHAR(2) NOT NULL DEFAULT '=',
                           value VARCHAR(255) NOT NULL,
                           enable TINYINT(4) NOT NULL) DEFAULT CHARACTER SET latin1;

DROP TABLE IF EXISTS admlog;
CREATE TABLE admlog (id INTEGER(11) PRIMARY KEY AUTO_INCREMENT,
                     console VARCHAR(80) NOT NULL,
                     info VARCHAR(255) NOT NULL,
                     timestamp INTEGER(11) NOT NULL DEFAULT 0) DEFAULT CHARACTER SET latin1;

DROP TABLE IF EXISTS radius_postauth;
CREATE TABLE radius_postauth (id INTEGER(11) PRIMARY KEY AUTO_INCREMENT,
                              user VARCHAR(64) NOT NULL,
                              pass VARCHAR(64) NOT NULL,
                              sucess TINYINT(4) NOT NULL DEFAULT 0,
                              CallingStationId VARCHAR(50) NOT NULL,
                              CalledStationId VARCHAR(50) NOT NULL) DEFAULT CHARACTER SET latin1;

DROP TABLE IF EXISTS radius_acct;
CREATE TABLE radius_acct (RadAcctId BIGINT(21) PRIMARY KEY AUTO_INCREMENT,
                          UserName VARCHAR(64) NOT NULL,
                          FramedIPAddress VARCHAR(15) NOT NULL,
                          CallingStationId VARCHAR(50) NOT NULL,
                          CalledStationId VARCHAR(255),
                          AcctStartTime DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
                          AcctStopTime DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00') DEFAULT CHARACTER SET latin1;

DROP TABLE IF EXISTS clientes;
CREATE TABLE clientes (id INTEGER(11) PRIMARY KEY AUTO_INCREMENT,
                       status TINYINT(4) NOT NULL,
                       nome VARCHAR(80) NOT NULL,
                       sexo CHAR(1) NOT NULL DEFAULT 'M',
                       endereco VARCHAR(80) NOT NULL,
                       numero VARCHAR(20) NOT NULL,
                       complemento VARCHAR(20) NOT NULL,
                       referencia VARCHAR(255) NOT NULL,
                       observacao TEXT) DEFAULT CHARACTER SET latin1;
