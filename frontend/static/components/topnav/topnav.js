/*
文件名称: topnav.js
完整存储路径: frontend/static/components/topnav/topnav.js
功能说明:
    封装顶部导航栏交互逻辑，包含全屏切换、用户下拉菜单显示以及触发侧边栏折叠。
    内部状态通过自定义事件传递，不直接暴露内部状态。
使用说明:
    在 HTML 文件中正确引入此脚本文件，确保对应元素存在。
*/

document.addEventListener('DOMContentLoaded', () => {
  // 侧边栏折叠按钮事件绑定
  const toggleSidebarBtn = document.getElementById('toggleSidebar');
  if (toggleSidebarBtn) {
    toggleSidebarBtn.addEventListener('click', () => {
      console.log('点击折叠菜单按钮');
      document.dispatchEvent(new CustomEvent('visionhealth:toggle-sidebar'));
    });
  } else {
    console.error('未找到 ID 为 toggleSidebar 的元素');
  }

  // 全屏按钮事件绑定
  const fullscreenBtn = document.getElementById('fullscreenBtn');
  if (fullscreenBtn) {
    fullscreenBtn.addEventListener('click', async () => {
      try {
        if (!document.fullscreenElement) {
          await document.documentElement.requestFullscreen();
          fullscreenBtn.innerHTML = '<i class="bi bi-fullscreen-exit"></i>';
        } else {
          await document.exitFullscreen();
          fullscreenBtn.innerHTML = '<i class="bi bi-fullscreen"></i>';
        }
        console.log('全屏切换成功');
      } catch (err) {
        console.error('全屏请求错误:', err);
      }
    });
  } else {
    console.error('未找到 ID 为 fullscreenBtn 的元素');
  }

  // 用户头像下拉菜单逻辑
  const userMenu = document.querySelector('.visionhealth-topnav__user-menu');
  const dropdown = document.querySelector('.visionhealth-topnav__dropdown');
  if (userMenu && dropdown) {
    userMenu.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation(); // 防止事件被多次触发
      dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
      console.log('用户头像点击，下拉菜单状态：', dropdown.style.display);
    });
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.visionhealth-topnav__user-menu')) {
        if (dropdown.style.display === 'block') {
          dropdown.style.display = 'none';
          console.log('外部点击，关闭下拉菜单');
        }
      }
    });
  } else {
    console.error('用户下拉菜单元素缺失');
  }
});
