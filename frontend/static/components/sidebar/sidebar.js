// 文件名称：sidebar.js
// 完整存储路径：E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\frontend\static\components\sidebar\sidebar.js
// 功能说明：处理侧边栏组件的动态菜单生成和交互逻辑
// 使用方法：
// - 在 HTML 文件中引入此 JavaScript 文件，确保路径正确。
// - 使用相应的 ID 和类名来绑定事件。

document.addEventListener('DOMContentLoaded', () => {
    const sidebarMenu = document.querySelector('.sidebar-menu');

    // 从后端获取菜单数据
    fetch('/api/menu')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            generateMenu(data);
        })
        .catch(error => {
            console.error("Error fetching menu data:", error);
        });

    function generateMenu(menuData) {
        menuData.forEach(menuItem => {
            const menuLi = document.createElement('li');
            menuLi.classList.add('menu-item');

            const menuLink = document.createElement('a');
            menuLink.href = menuItem.link;
            menuLink.innerHTML = `
                <i class="bi ${menuItem.icon}"></i>
                <span class="menu-text">${menuItem.title}</span>
            `;
            menuLi.appendChild(menuLink);

            if (menuItem.sub_menu && menuItem.sub_menu.length > 0) {
                const submenuUl = document.createElement('ul');
                submenuUl.classList.add('submenu');

                menuItem.sub_menu.forEach(subItem => {
                    const subMenuLi = document.createElement('li');
                    const subMenuLink = document.createElement('a');
                    subMenuLink.href = subItem.link;
                    subMenuLink.innerHTML = `
                        <i class="bi ${subItem.icon}"></i>
                        <span class="menu-text">${subItem.title}</span>
                    `;
                    subMenuLi.appendChild(subMenuLink);
                    submenuUl.appendChild(subMenuLi);
                });

                menuLi.appendChild(submenuUl);
            }

            sidebarMenu.appendChild(menuLi);
        });

        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const submenu = item.querySelector('.submenu');
                if (submenu) {
                    submenu.classList.toggle('active');
                }
            });
        });
    }

    // 折叠/展开侧边栏
    function toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const isCollapsed = sidebar.getAttribute('data-collapsed') === 'true';
        sidebar.setAttribute('data-collapsed', !isCollapsed);
    }

    // 绑定折叠/展开事件
    document.querySelectorAll('.toggle-collapse').forEach(button => {
        button.addEventListener('click', toggleSidebar);
    });
});