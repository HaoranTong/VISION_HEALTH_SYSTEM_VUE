/*
文件名称: sidebar.js
完整存储路径: frontend/static/components/sidebar/sidebar.js
功能说明:
    封装侧边栏交互逻辑，动态加载菜单数据，并实现二级子菜单的展开/收起。
    内部状态通过自定义事件和 CSS 变量传递，不暴露全局状态。
使用说明:
    在页面加载时自动执行，无需额外调用。确保 HTML 中已包含
    "visionhealth-sidebar" 类的组件容器。
*/

document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.querySelector('.visionhealth-sidebar');
  const menuContainer = document.querySelector('.visionhealth-sidebar__menu');

  console.log('Sidebar 初始化:', sidebar);

  // 自定义事件监听：切换侧边栏折叠状态
  document.addEventListener('visionhealth:toggle-sidebar', () => {
    const collapsed = sidebar.getAttribute('data-collapsed') === 'true';
    console.log('侧边栏折叠事件触发，当前状态:', collapsed);
    sidebar.setAttribute('data-collapsed', (!collapsed).toString());
    const newWidth = !collapsed
      ? getComputedStyle(document.documentElement)
          .getPropertyValue('--visionhealth-sidebar-collapsed-width')
      : getComputedStyle(document.documentElement)
          .getPropertyValue('--visionhealth-sidebar-width');
    document.documentElement.style.setProperty('--current-sidebar-width', newWidth);
    console.log('更新后 --current-sidebar-width:', newWidth);
  });

  // 动态加载菜单数据并生成 HTML 结构
  fetch('/api/menu')
    .then(response => response.json())
    .then(data => {
      console.log('菜单数据加载成功:', data);
      menuContainer.innerHTML = data.map(item => {
        if (item.sub_menu && item.sub_menu.length > 0) {
          return `
            <li class="visionhealth-sidebar__menu-item has-submenu">
              <a href="${item.link}" class="visionhealth-sidebar__menu-link visionhealth-sidebar__menu-toggle">
                <i class="bi ${item.icon} visionhealth-sidebar__menu-icon"></i>
                <span class="visionhealth-sidebar__menu-text">${item.title}</span>
                <i class="bi bi-chevron-down visionhealth-sidebar__submenu-icon"></i>
              </a>
              <ul class="visionhealth-sidebar__submenu">
                ${item.sub_menu.map(subItem => `
                  <li class="visionhealth-sidebar__menu-item">
                    <a href="${subItem.link}" class="visionhealth-sidebar__menu-link">
                      <i class="bi ${subItem.icon} visionhealth-sidebar__menu-icon"></i>
                      <span class="visionhealth-sidebar__menu-text">${subItem.title}</span>
                    </a>
                  </li>
                `).join('')}
              </ul>
            </li>
          `;
        } else {
          return `
            <li class="visionhealth-sidebar__menu-item">
              <a href="${item.link}" class="visionhealth-sidebar__menu-link">
                <i class="bi ${item.icon} visionhealth-sidebar__menu-icon"></i>
                <span class="visionhealth-sidebar__menu-text">${item.title}</span>
              </a>
            </li>
          `;
        }
      }).join('');

      // 绑定点击事件：切换二级菜单显示
      const menuToggles = document.querySelectorAll('.visionhealth-sidebar__menu-toggle');
      menuToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
          e.preventDefault();
          const parentItem = toggle.parentElement;
          parentItem.classList.toggle('active');
          console.log('切换子菜单状态:', parentItem.classList.contains('active'));
        });
      });
    })
    .catch(error => {
      console.error('菜单加载错误:', error);
      menuContainer.innerHTML = `
        <li class="visionhealth-sidebar__menu-item">
          <span class="visionhealth-sidebar__menu-text">
            菜单加载失败: ${error.message}
          </span>
        </li>`;
    });
});
