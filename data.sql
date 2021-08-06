BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "door_logs" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"room"	VARCHAR(10) NOT NULL,
	"opened_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	"closed_at"	DATETIME,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER,
	"code"	VARCHAR(50),
	"fullname"	VARCHAR(50),
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "door_logs" ("id","user_id","room","opened_at","closed_at") VALUES (1,1,'I3.302','2021-08-06 19:21:27','2021-08-06 19:21:27');
INSERT INTO "door_logs" ("id","user_id","room","opened_at","closed_at") VALUES (2,1,'I3.302','2021-08-06 19:22:07',NULL);
INSERT INTO "users" ("id","code","fullname") VALUES (1,'1824801030053','Dương Lê Phước Trung');
INSERT INTO "users" ("id","code","fullname") VALUES (2,'1824801030067','Trần Minh Hiếu');
INSERT INTO "users" ("id","code","fullname") VALUES (3,'1824801030060','Lê Thành Đạt');
INSERT INTO "users" ("id","code","fullname") VALUES (4,'1824801030015','Nguyễn Ngọc Minh');
COMMIT;
