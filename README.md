[README.md](https://github.com/user-attachments/files/29940212/README.md)
# Simple-University-Management-System
Design and Implementation of Simple University Management System Based on SQL Server and PyCharm
# 高校教师信息管理系统

基于 **SQL Server + Python Flask** 的高校教师信息管理 Web 系统，涵盖教师、学院、系、课程、教学任务、科研成果与考勤等全业务场景，配套数据库设计与后台管理界面。

## 功能特性

- **管理员登录**：基于 Admin 表的账号密码校验，会话跳转至管理控制台
- **数据概览控制台**：展示教师总数、学院列表、最新考勤记录
- **教师管理**：教师信息的列表查看、新增、删除
- **教师搜索**：按姓名模糊查询（调用存储过程 `GetTeacherByName`）

## 技术栈

| 类别 | 技术 |
|------|------|
| 数据库 | SQL Server（T-SQL） |
| 后端 | Python 3、Flask |
| 数据访问 | pyodbc、pandas |
| 连接方式 | Windows 身份认证（Trusted_Connection） |
| 前端 | 服务端渲染 HTML 模板（Flask 内联模板） |

## 目录结构

```
.
├── 脚本.sql                # 数据库建库、建表、索引、视图、存储过程、触发器、函数及初始数据
└── 高校教师管理系统.py     # Flask 后端应用，提供登录、控制台、教师增删查接口
```

## 数据库设计

数据库名：`TeacherInfoDB`，共 8 张核心数据表：

| 表名 | 说明 |
|------|------|
| `Admin` | 系统管理员账号 |
| `Teacher` | 教师基本信息（账号、姓名、性别、出生日期、电话、邮箱、照片） |
| `College` | 学院信息 |
| `Department` | 系信息（外键关联 College） |
| `Course` | 课程信息（外键关联 Department） |
| `TeachingTask` | 教学任务（关联 Teacher 与 Course） |
| `Research` | 教师科研成果 |
| `Attendance` | 教师考勤记录 |

数据库对象还包括：

- **索引**：在 `Teacher(Account)`、`Teacher(Name)`、`Course(Name)`、`Research(Title)` 上建立索引，优化常用查询
- **视图** `TeacherDetails`：联表输出教师及其所属系、学院的详细信息
- **存储过程** `GetTeacherByName`：按教师姓名模糊查询
- **触发器** `TR_Teacher_Insert`：教师插入时输出日志提示
- **函数** `CalculateAge`：根据出生日期计算年龄

## 环境准备

1. 安装 SQL Server（本地默认实例或命名实例如 `SQLEXPRESS`）
2. 安装 ODBC Driver 17 for SQL Server
3. 安装 Python 依赖：

```bash
pip install flask pyodbc pandas
```

## 部署与运行

1. 在 SQL Server 中执行 `脚本.sql` 完成建库与初始化数据
2. 编辑 `高校教师管理系统.py` 中的 `SERVER` 参数：

```python
SERVER = 'localhost'            # 本地默认实例
# SERVER = 'localhost\\SQLEXPRESS'  # 本地命名实例
```

3. 启动应用：

```bash
python 高校教师管理系统.py
```

4. 浏览器访问 `http://localhost:5000`

## 使用说明

- 初始管理员账号：`Admin`
- 初始密码：`123`

登录后可进入管理控制台，进行教师信息的查看、新增、删除与按姓名搜索。

## 说明

本项目用于演示关系数据库设计、SQL 对象开发（视图/存储过程/触发器/函数）与 Python 后端数据访问的完整流程。
