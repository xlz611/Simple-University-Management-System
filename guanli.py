from flask import Flask, render_template_string, request, redirect, url_for, flash
import pyodbc
import pandas as pd
import sys

# 初始化 Flask 应用
app = Flask(__name__)
app.secret_key = 'teacher_info_management_system_2025'  # 用于 flash 消息


# --------------------------
# 数据库连接配置（仅需修改SERVER参数！！！）
# --------------------------
def get_db_connection():
    """创建并返回数据库连接（Windows身份认证，无需账号密码）"""
    try:
        # ==== 仅需修改这1行 ====
        SERVER = 'localhost'  # 本地默认实例写localhost，命名实例写 localhost\SQLEXPRESS
        # =====================

        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={SERVER};'
            'DATABASE=TeacherInfoDB;'
            'Trusted_Connection=yes;'  # 核心：Windows身份认证
            'Encrypt=no;'  # 关闭加密（本地测试用）
        )
        return conn
    except pyodbc.Error as e:
        error_msg = f"数据库连接失败: {e.args[1]}"
        print(error_msg)
        # 常见错误提示优化
        if "找不到服务器" in error_msg or "实例" in error_msg:
            print("→ 原因：SERVER参数错误（比如漏写\\SQLEXPRESS）")
        elif "ODBC Driver 17" in error_msg:
            print("→ 原因：未安装ODBC Driver 17 for SQL Server")
        elif "拒绝访问" in error_msg:
            print("→ 原因：当前Windows账号无SQL Server访问权限")
        return None
    except Exception as e:
        print(f"未知错误: {str(e)}")
        return None


# --------------------------
# HTML 模板字符串
# --------------------------
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>教师信息管理系统 - 登录</title>
    <style>
        .login-box { width: 300px; margin: 100px auto; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input { width: 100%; padding: 8px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .flash { color: red; text-align: center; margin-bottom: 15px; }
        .tips { color: #666; font-size: 12px; text-align: center; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2 align="center">管理员登录</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="flash">{{ messages[0] }}</div>
            {% endif %}
        {% endwith %}
        <form method="POST" action="{{ url_for('login') }}">
            <div class="form-group">
                <label>账号：</label>
                <input type="text" name="account" value="Admin" required>
            </div>
            <div class="form-group">
                <label>密码：</label>
                <input type="password" name="password" value="123" required>
            </div>
            <button type="submit">登录</button>
        </form>
        <div class="tips">初始账号：Admin | 初始密码：123</div>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>管理控制台</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; text-decoration: none; color: #007bff; }
        .card { border: 1px solid #ccc; border-radius: 5px; padding: 15px; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    </style>
</head>
<body>
    <div class="nav">
        <a href="{{ url_for('dashboard') }}">控制台</a>
        <a href="{{ url_for('teachers') }}">教师管理</a>
        <a href="{{ url_for('index') }}">退出登录</a>
    </div>

    <h1>教师信息管理系统</h1>

    <div class="card">
        <h3>数据概览</h3>
        <p>教师总数：{{ teacher_count }}</p>
    </div>

    <div class="card">
        <h3>学院列表</h3>
        <table>
            <tr>
                <th>学院ID</th>
                <th>学院名称</th>
                <th>描述</th>
            </tr>
            {% for college in colleges %}
            <tr>
                <td>{{ college.CollegeID }}</td>
                <td>{{ college.Name }}</td>
                <td>{{ college.Description }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <div class="card">
        <h3>最新考勤记录</h3>
        <table>
            <tr>
                <th>考勤ID</th>
                <th>教师ID</th>
                <th>日期</th>
                <th>状态</th>
            </tr>
            {% for att in attendance %}
            <tr>
                <td>{{ att.AttendanceID }}</td>
                <td>{{ att.TeacherID }}</td>
                <td>{{ att.Date }}</td>
                <td>{{ att.Status }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

TEACHERS_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>教师管理</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; text-decoration: none; color: #007bff; }
        .search-form { margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        .btn { padding: 5px 10px; text-decoration: none; border-radius: 3px; }
        .btn-add { background: #28a745; color: white; }
        .btn-delete { background: #dc3545; color: white; }
        .flash { color: green; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="nav">
        <a href="{{ url_for('dashboard') }}">控制台</a>
        <a href="{{ url_for('teachers') }}">教师管理</a>
        <a href="{{ url_for('index') }}">退出登录</a>
    </div>

    <h1>教师管理</h1>

    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <div class="flash">{{ messages[0] }}</div>
        {% endif %}
    {% endwith %}

    <!-- 搜索表单 -->
    <form class="search-form" method="POST" action="{{ url_for('search_teacher') }}">
        <input type="text" name="teacher_name" placeholder="输入教师姓名搜索">
        <button type="submit">搜索</button>
        <a href="{{ url_for('add_teacher') }}" class="btn btn-add">添加教师</a>
    </form>

    <!-- 教师列表 -->
    <table>
        <tr>
            <th>教师ID</th>
            <th>账号</th>
            <th>姓名</th>
            <th>性别</th>
            <th>出生日期</th>
            <th>电话</th>
            <th>邮箱</th>
            <th>所属学院</th>
            <th>操作</th>
        </tr>
        {% for teacher in teachers %}
        <tr>
            <td>{{ teacher.TeacherID }}</td>
            <td>{{ teacher.Account }}</td>
            <td>{{ teacher.Name }}</td>
            <td>{{ teacher.Gender }}</td>
            <td>{{ teacher.BirthDate }}</td>
            <td>{{ teacher.Phone }}</td>
            <td>{{ teacher.Email }}</td>
            <td>{{ teacher.CollegeName if teacher.CollegeName else '未分配' }}</td>
            <td>
                <a href="{{ url_for('delete_teacher', teacher_id=teacher.TeacherID) }}" class="btn btn-delete" onclick="return confirm('确定删除？')">删除</a>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

ADD_TEACHER_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>添加教师</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; text-decoration: none; color: #007bff; }
        .form-box { width: 400px; margin: 0 auto; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input { width: 100%; padding: 8px; box-sizing: border-box; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .flash { color: red; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="nav">
        <a href="{{ url_for('dashboard') }}">控制台</a>
        <a href="{{ url_for('teachers') }}">教师管理</a>
    </div>

    <div class="form-box">
        <h2>添加新教师</h2>

        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="flash">{{ messages[0] }}</div>
            {% endif %}
        {% endwith %}

        <form method="POST" action="{{ url_for('add_teacher') }}">
            <div class="form-group">
                <label>账号：</label>
                <input type="text" name="account" required>
            </div>
            <div class="form-group">
                <label>密码：</label>
                <input type="password" name="password" required>
            </div>
            <div class="form-group">
                <label>姓名：</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>性别：</label>
                <input type="text" name="gender" placeholder="男/女" required>
            </div>
            <div class="form-group">
                <label>出生日期：</label>
                <input type="date" name="birthdate" required>
            </div>
            <div class="form-group">
                <label>电话：</label>
                <input type="text" name="phone" required>
            </div>
            <div class="form-group">
                <label>邮箱：</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>照片URL（可选）：</label>
                <input type="text" name="image_url" placeholder="/images/default.jpg">
            </div>
            <button type="submit">提交</button>
        </form>
    </div>
</body>
</html>
"""


# --------------------------
# 路由与视图函数
# --------------------------
@app.route('/')
def index():
    """首页 - 管理员登录"""
    return render_template_string(LOGIN_TEMPLATE)


@app.route('/login', methods=['POST'])
def login():
    """管理员登录验证"""
    account = request.form.get('account')
    password = request.form.get('password')

    conn = get_db_connection()
    if not conn:
        flash('数据库连接失败，请检查代码中的SERVER参数！')
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Admin WHERE Account=? AND Password=?", (account, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            return redirect(url_for('dashboard'))
        else:
            flash('账号或密码错误（初始账号：Admin，密码：123）！')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'登录验证失败: {str(e)}')
        conn.close()
        return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """管理控制台 - 显示核心数据概览"""
    conn = get_db_connection()
    if not conn:
        flash('数据库连接失败，请检查SERVER参数！')
        return redirect(url_for('index'))

    try:
        # 获取教师总数
        teacher_count = pd.read_sql("SELECT COUNT(*) AS count FROM Teacher", conn)['count'].iloc[0]
        # 获取学院列表
        colleges = pd.read_sql("SELECT * FROM College", conn)
        # 获取最新考勤记录
        attendance = pd.read_sql("SELECT TOP 5 * FROM Attendance ORDER BY Date DESC", conn)

        conn.close()

        return render_template_string(DASHBOARD_TEMPLATE,
                                      teacher_count=teacher_count,
                                      colleges=colleges.to_dict('records'),
                                      attendance=attendance.to_dict('records'))
    except Exception as e:
        flash(f'加载控制台数据失败: {str(e)}')
        conn.close()
        return redirect(url_for('index'))


@app.route('/teachers')
def teachers():
    """教师列表页面"""
    conn = get_db_connection()
    if not conn:
        flash('数据库连接失败，请检查SERVER参数！')
        return redirect(url_for('index'))

    try:
        # 使用视图获取教师详细信息
        teachers_df = pd.read_sql("SELECT * FROM TeacherDetails", conn)
        conn.close()

        return render_template_string(TEACHERS_TEMPLATE, teachers=teachers_df.to_dict('records'))
    except Exception as e:
        flash(f'加载教师列表失败: {str(e)}')
        conn.close()
        return redirect(url_for('dashboard'))


@app.route('/teacher/add', methods=['GET', 'POST'])
def add_teacher():
    """添加教师"""
    if request.method == 'GET':
        return render_template_string(ADD_TEACHER_TEMPLATE)

    # POST 请求 - 提交表单
    conn = get_db_connection()
    if not conn:
        flash('数据库连接失败，请检查SERVER参数！')
        return redirect(url_for('add_teacher'))

    try:
        account = request.form.get('account')
        password = request.form.get('password')
        name = request.form.get('name')
        gender = request.form.get('gender')
        birthdate = request.form.get('birthdate')
        phone = request.form.get('phone')
        email = request.form.get('email')
        image_url = request.form.get('image_url', '/images/default.jpg')

        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO Teacher (Account, Password, Name, Gender, BirthDate, Phone, Email, ImageUrl)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                       """, (account, password, name, gender, birthdate, phone, email, image_url))
        conn.commit()
        conn.close()

        flash('教师信息添加成功！')
        return redirect(url_for('teachers'))

    except Exception as e:
        flash(f'添加失败：{str(e)}')
        conn.close()
        return redirect(url_for('add_teacher'))


@app.route('/teacher/delete/<int:teacher_id>')
def delete_teacher(teacher_id):
    """删除教师"""
    conn = get_db_connection()
    if not conn:
        flash('数据库连接失败，请检查SERVER参数！')
        return redirect(url_for('teachers'))

    try:
        cursor = conn.cursor()
        # 先删除关联数据（避免外键约束报错）
        cursor.execute("DELETE FROM TeachingTask WHERE TeacherID=?", (teacher_id,))
        cursor.execute("DELETE FROM Research WHERE TeacherID=?", (teacher_id,))
        cursor.execute("DELETE FROM Attendance WHERE TeacherID=?", (teacher_id,))
        # 删除教师主数据
        cursor.execute("DELETE FROM Teacher WHERE TeacherID=?", (teacher_id,))

        conn.commit()
        conn.close()

        flash('教师信息删除成功！')
    except Exception as e:
        flash(f'删除失败：{str(e)}')
        conn.close()

    return redirect(url_for('teachers'))


@app.route('/teacher/search', methods=['POST'])
def search_teacher():
    """搜索教师（调用存储过程）"""
    teacher_name = request.form.get('teacher_name', '')

    conn = get_db_connection()
    if not conn:
        flash('数据库连接失败，请检查SERVER参数！')
        return redirect(url_for('teachers'))

    try:
        # 调用存储过程
        teachers_df = pd.read_sql("EXEC GetTeacherByName @TeacherName=?", conn, params=(teacher_name,))
        conn.close()

        return render_template_string(TEACHERS_TEMPLATE, teachers=teachers_df.to_dict('records'))
    except Exception as e:
        flash(f'搜索失败：{str(e)}')
        conn.close()
        return redirect(url_for('teachers'))


# --------------------------
# 启动应用
# --------------------------
if __name__ == '__main__':
    # 初始化提示
    print("=" * 60)
    print("⚠️  Windows身份认证版 - 仅需修改SERVER参数：")
    print("   - 本地默认实例：SERVER = 'localhost'")
    print("   - 本地命名实例（如Express）：SERVER = 'localhost\\SQLEXPRESS'")
    print("=" * 60)

    # 设置 pandas 显示选项（避免警告）
    pd.set_option('future.no_silent_downcasting', True)

    # 修复 Windows 下的编码问题
    if sys.platform == 'win32':
        import subprocess

        subprocess.call('chcp 65001', shell=True)

    # 启动 Flask 应用
    print("\n服务器启动中... 访问地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
