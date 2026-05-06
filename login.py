import getpass
from supabase import create_client, Client

# --- 配置区域 ---
url: str = "https://zrdyupxefsridxdubfmb.supabase.co"
key: str = "sb_publishable_xAGCOI7ESqFqXC5R4rCVkA_hXHUBXQ8"
supabase: Client = create_client(url, key)

def get_input(prompt, hide=False):
    """辅助函数：处理普通输入或隐藏输入"""
    if hide:
        return getpass.getpass(prompt)
    else:
        return input(prompt).strip()

def perform_login_action(email, password):
    """
    执行登录的具体动作（验证密码 -> 显示结果）
    返回 True 表示登录成功，False 表示失败
    """
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email, 
            "password": password
        })
        print("✅ 登录成功！")
        return True # 👈 登录成功，返回 True
        
    except Exception:
        print("❌ 登录失败：密码错误。")
        return False # 👈 登录失败，返回 False

def register_and_auto_login():
    """
    注册流程：注册成功后，直接复用账号信息进行登录
    """
    print("\n--- ✨ 新用户注册 ---")
    email = get_input("请输入要注册的邮箱: ")
    
    if "@" not in email:
        print("❌ 邮箱格式不正确！")
        return False # 注册失败

    # 1. 设置密码
    while True:
        password = get_input("设置密码: ", hide=True)
        confirm_password = get_input("确认密码: ", hide=True)
        if password == confirm_password:
            break
        else:
            print("❌ 两次输入的密码不一致，请重试。")

    # 2. 设置密码提示
    password_hint = get_input("设置密码提示: ")

    # 3. 调用 Supabase 注册
    try:
        print("正在创建账户...")
        auth_response = supabase.auth.sign_up({
            "email": email, 
            "password": password
        })
        
        if auth_response.user:
            user = auth_response.user
            # 写入密码提示到 profiles 表
            supabase.table("profiles").update({
                "password_hint": password_hint
            }).eq("id", user.id).execute()
            
            print("✅ 注册成功！正在为您自动登录...")
            # 【修改点】：返回登录动作的结果
            return perform_login_action(email, password)
        else:
            print("❌ 注册失败，请检查邮箱是否已被占用。")
            return False
            
    except Exception as e:
        print(f"❌ 注册异常: {e}")
        return False

def manual_login_flow(email):
    """
    老用户手动登录流程：查提示 -> 输密码 -> 登录
    """
    print("\n--- 🔑 用户登录 ---")
    
    # 1. 先查询并显示密码提示
    response = supabase.table("profiles").select("password_hint").eq("email", email).execute()
    
    if response.data and len(response.data) > 0:
        # 老用户
        hint = response.data[0].get("password_hint")
        print(f"ℹ️  检测到账号已注册。")
        print(f"🔑 密码提示: {hint}")
        
        # 输入密码
        password = get_input("请输入密码: ", hide=True)
        
        # 【修改点】：返回登录动作的结果
        return perform_login_action(email, password)
            
    else:
        # 邮箱不存在
        print("❌ 未找到该邮箱的注册记录。")
        print("💡 提示：如果是第一次使用，请输入 1 进行注册。")
        return False

def main():
    """主程序入口"""
    print("========================================")
    print("      欢迎使用 Supabase 演示系统        ")
    print("========================================")
    
    while True:
        print("\n如果您注册过本系统，请输入注册的邮箱地址登录。")
        print("第一次使用请输入数字 1 开启登录流程")
        
        choice = input(">>> ").strip()
        
        is_login_success = False # 用于接收登录结果的变量
        
        if choice == "1":
            # 输入 1：走注册流程（注册完自动登录）
            is_login_success = register_and_auto_login()
        else:
            # 输入其他：走手动登录流程
            if "@" in choice:
                is_login_success = manual_login_flow(choice)
            else:
                print("❌ 请输入有效的邮箱地址，或输入 1 注册。")
                continue # 输入无效，直接进入下一次循环
        
        # 【核心修改点】：检查登录是否成功
        if is_login_success:
            # 如果成功，就跳出 while 循环
            break

    # 👇 循环结束后，执行登录后的功能
    print("\n完成登录，这里开始执行程序功能部分")
    # ... 这里可以写你的程序主功能，比如设备绑定、数据管理等 ...

# --- 运行程序 ---
if __name__ == "__main__":
    main()
