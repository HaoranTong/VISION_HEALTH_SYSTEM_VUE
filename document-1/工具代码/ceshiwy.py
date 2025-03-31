from flask import Flask, render_template_string

app = Flask(__name__)


@app.route("/")
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>近视预防干预系统</title>
      <style>
        /* 全局样式重置 */
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        body {
          font-family: Arial, sans-serif;
          background-color: #f4f4f4;
        }
        /* 顶部区域 */
        header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          background-color: #333;
          color: #fff;
          padding: 10px 20px;
        }
        header .logo {
          font-size: 24px;
          font-weight: bold;
        }
        header .top-nav {
          display: flex;
          align-items: center;
        }
        header .top-nav a {
          color: #fff;
          text-decoration: none;
          margin-left: 20px;
        }
        header .top-nav input[type="text"] {
          margin-left: 20px;
          padding: 5px 10px;
          border: none;
          border-radius: 4px;
        }
        /* 整体布局：侧边栏 + 主内容 */
        #container {
          display: flex;
          min-height: calc(100vh - 60px); /* 顶部区域高度约60px */
        }
        /* 侧边栏 */
        aside {
          width: 240px;
          background-color: #444;
          color: #fff;
          padding: 20px;
        }
        aside nav ul {
          list-style: none;
        }
        aside nav ul li {
          margin-bottom: 15px;
        }
        aside nav ul li a {
          color: #fff;
          text-decoration: none;
          display: block;
          padding: 10px;
          border-radius: 4px;
          transition: background-color 0.3s;
        }
        aside nav ul li a:hover,
        aside nav ul li a.active {
          background-color: #666;
        }
        /* 主内容区 */
        main {
          flex: 1;
          padding: 20px;
          background-color: #fff;
        }
        /* 响应式设计 */
        @media screen and (max-width: 768px) {
          #container {
            flex-direction: column;
          }
          aside {
            width: 100%;
          }
        }
      </style>
    </head>
    <body>
      <!-- 顶部区域 -->
      <header>
        <div class="logo">近视预防干预系统</div>
        <div class="top-nav">
          <a href="#">首页</a>
          <a href="#">产品介绍</a>
          <a href="#">服务支持</a>
          <a href="#">联系我们</a>
          <input type="text" placeholder="搜索...">
        </div>
      </header>

      <!-- 主体区域：侧边栏和数据展示区 -->
      <div id="container">
        <!-- 侧边栏导航 -->
        <aside>
          <nav>
            <ul>
              <li><a href="#" class="active">仪表盘</a></li>
              <li><a href="#">统计分析</a></li>
              <li><a href="#">参数设置</a></li>
              <li><a href="#">用户管理</a></li>
              <li><a href="#">系统日志</a></li>
            </ul>
          </nav>
        </aside>

        <!-- 主内容区域，此处为占位符 -->
        <main>
          <h2>数据展示区域</h2>
          <p>（此区域内容根据实际业务需求进行开发）</p>
        </main>
      </div>
    </body>
    </html>
    """
    return render_template_string(html_content)


if __name__ == "__main__":
    app.run(debug=True)
