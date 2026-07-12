CREATE DATABASE TeacherInfoDB;
GO

USE TeacherInfoDB;
GO

-- 管理员
CREATE TABLE Admin (
    AdminID INT IDENTITY(1,1) PRIMARY KEY, -- 管理员ID
    Account NVARCHAR(50) NOT NULL, -- 账号
    Password NVARCHAR(50) NOT NULL, -- 密码
    Name NVARCHAR(50) NOT NULL -- 姓名
);
GO

-- 教师
CREATE TABLE Teacher (
    TeacherID INT IDENTITY(1,1) PRIMARY KEY, -- 教师ID
    Account NVARCHAR(50) NOT NULL, -- 账号
    Password NVARCHAR(50) NOT NULL, -- 密码
    Name NVARCHAR(50) NOT NULL, -- 姓名
    Gender NVARCHAR(10), -- 性别
    BirthDate DATE, -- 出生日期
    Phone NVARCHAR(20), -- 电话
    Email NVARCHAR(100), -- 邮箱
    ImageUrl NVARCHAR(255) -- 照片URL
);
GO

-- 学院
CREATE TABLE College (
    CollegeID INT IDENTITY(1,1) PRIMARY KEY, -- 学院ID
    Name NVARCHAR(100) NOT NULL, -- 学院名称
    Description NVARCHAR(500) -- 学院描述
);
GO

-- 系
CREATE TABLE Department (
    DepartmentID INT IDENTITY(1,1) PRIMARY KEY, -- 系ID
    Name NVARCHAR(100) NOT NULL, -- 系名称
    CollegeID INT NOT NULL, -- 学院ID
    CONSTRAINT FK_Department_College FOREIGN KEY (CollegeID) REFERENCES College(CollegeID) ON DELETE CASCADE
);
GO

-- 课程
CREATE TABLE Course (
    CourseID INT IDENTITY(1,1) PRIMARY KEY, -- 课程ID
    Name NVARCHAR(100) NOT NULL, -- 课程名称
    Description NVARCHAR(500), -- 课程描述
    Credit INT NOT NULL, -- 学分
    DepartmentID INT NOT NULL, -- 系ID
    CONSTRAINT FK_Course_Department FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID) ON DELETE NO ACTION
);
GO

-- 教学任务
CREATE TABLE TeachingTask (
    TaskID INT IDENTITY(1,1) PRIMARY KEY, -- 任务ID
    TeacherID INT NOT NULL, -- 教师ID
    CourseID INT NOT NULL, -- 课程ID
    Semester NVARCHAR(50) NOT NULL, -- 学期
    CONSTRAINT FK_TeachingTask_Teacher FOREIGN KEY (TeacherID) REFERENCES Teacher(TeacherID) ON DELETE NO ACTION,
    CONSTRAINT FK_TeachingTask_Course FOREIGN KEY (CourseID) REFERENCES Course(CourseID) ON DELETE NO ACTION
);
GO

-- 科研成果
CREATE TABLE Research (
    ResearchID INT IDENTITY(1,1) PRIMARY KEY, -- 成果ID
    TeacherID INT NOT NULL, -- 教师ID
    Title NVARCHAR(200) NOT NULL, -- 成果标题
    Description NVARCHAR(1000), -- 成果描述
    PublishDate DATE, -- 发布日期
    FileUrl NVARCHAR(255), -- 文件URL
    CONSTRAINT FK_Research_Teacher FOREIGN KEY (TeacherID) REFERENCES Teacher(TeacherID) ON DELETE CASCADE
);
GO

-- 考勤记录
CREATE TABLE Attendance (
    AttendanceID INT IDENTITY(1,1) PRIMARY KEY, -- 考勤ID
    TeacherID INT NOT NULL, -- 教师ID
    Date DATE NOT NULL, -- 日期
    Status NVARCHAR(20) NOT NULL, -- 状态
    CONSTRAINT FK_Attendance_Teacher FOREIGN KEY (TeacherID) REFERENCES Teacher(TeacherID) ON DELETE NO ACTION
);
GO

-- 索引
CREATE INDEX IX_Teacher_Account ON Teacher(Account);
GO
CREATE INDEX IX_Teacher_Name ON Teacher(Name);
GO
CREATE INDEX IX_Course_Name ON Course(Name);
GO
CREATE INDEX IX_Research_Title ON Research(Title);
GO

-- 视图：教师详细信息
CREATE VIEW TeacherDetails AS
SELECT 
    t.TeacherID,
    t.Account,
    t.Name,
    t.Gender,
    t.BirthDate,
    t.Phone,
    t.Email,
    d.Name AS DepartmentName,
    c.Name AS CollegeName
FROM Teacher t
LEFT JOIN TeachingTask tt ON t.TeacherID = tt.TeacherID
LEFT JOIN Course co ON tt.CourseID = co.CourseID
LEFT JOIN Department d ON co.DepartmentID = d.DepartmentID
LEFT JOIN College c ON d.CollegeID = c.CollegeID;
GO

-- 存储过程：根据教师姓名查询教师信息
CREATE PROCEDURE GetTeacherByName
    @TeacherName NVARCHAR(50)
AS
BEGIN
    SELECT * FROM Teacher WHERE Name LIKE '%' + @TeacherName + '%';
END;
GO

-- 触发器：插入教师时记录日志
CREATE TRIGGER TR_Teacher_Insert
ON Teacher
AFTER INSERT
AS
BEGIN
    PRINT '新教师信息已添加';
END;
GO

-- 函数：计算教师年龄
CREATE FUNCTION CalculateAge(@BirthDate DATE)
RETURNS INT
AS
BEGIN
    RETURN DATEDIFF(YEAR, @BirthDate, GETDATE());
END;
GO

-- 插入初始数据
INSERT INTO Admin (Account, Password, Name) VALUES ('Admin', '123', '管理员');
GO

INSERT INTO College (Name, Description) VALUES 
('计算机学院', '专注于计算机科学与技术'),
('经济管理学院', '培养经济管理人才'),
('外国语学院', '语言文化与翻译教学'),
('法学院', '法律理论与实务结合'),
('艺术学院', '艺术创作与设计');
GO

INSERT INTO Department (Name, CollegeID) VALUES 
('软件工程系', 1),
('网络工程系', 1),
('经济学系', 2),
('英语系', 3),
('美术系', 5);
GO

INSERT INTO Teacher (Account, Password, Name, Gender, BirthDate, Phone, Email, ImageUrl) VALUES 
('t1001', 'pass123', '张老师', '男', '1980-05-15', '13800138001', 'zhang@example.com', '/images/zhang.jpg'),
('t1002', 'pass123', '李老师', '女', '1975-08-20', '13800138002', 'li@example.com', '/images/li.jpg'),
('t1003', 'pass123', '王老师', '男', '1982-03-10', '13800138003', 'wang@example.com', '/images/wang.jpg'),
('t1004', 'pass123', '赵老师', '女', '1978-11-25', '13800138004', 'zhao@example.com', '/images/zhao.jpg'),
('t1005', 'pass123', '刘老师', '男', '1985-07-30', '13800138005', 'liu@example.com', '/images/liu.jpg');
GO

INSERT INTO Course (Name, Description, Credit, DepartmentID) VALUES 
('Java程序设计', 'Java语言与面向对象编程', 4, 1),
('数据库原理', '关系数据库设计与SQL', 3, 1),
('微观经济学', '市场经济基本理论', 3, 3),
('英语写作', '学术与商务英语写作', 2, 4),
('油画基础', '油画技法与创作', 2, 5);
GO

INSERT INTO TeachingTask (TeacherID, CourseID, Semester) VALUES 
(1, 1, '2023秋季'),
(2, 2, '2023秋季'),
(3, 3, '2023秋季'),
(4, 4, '2023秋季'),
(5, 5, '2023秋季');
GO

INSERT INTO Research (TeacherID, Title, Description, PublishDate, FileUrl) VALUES 
(1, '人工智能在教育中的应用', '探讨AI技术如何优化教学流程', '2023-01-10', '/files/ai_education.pdf'),
(2, '分布式系统性能优化', '研究提升分布式计算效率的方法', '2023-02-15', '/files/distributed_systems.pdf'),
(3, '市场经济改革研究', '分析中国经济改革历程与效果', '2023-03-20', '/files/market_economy.pdf'),
(4, '跨文化交际研究', '比较中西方沟通差异与策略', '2023-04-25', '/files/cross_culture.pdf'),
(5, '现代艺术流派分析', '20世纪主要艺术运动综述', '2023-05-30', '/files/art_movements.pdf');
GO

INSERT INTO Attendance (TeacherID, Date, Status) VALUES 
(1, '2023-09-01', '出勤'),
(2, '2023-09-01', '出勤'),
(3, '2023-09-01', '请假'),
(4, '2023-09-01', '出勤'),
(5, '2023-09-01', '迟到');
GO