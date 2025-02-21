// 文件名称: sidebar.js
// 保存路径: frontend/static/components/sidebar/sidebar.js

document.addEventListener('DOMContentLoaded', () => {
    const sidebarMenu = document.querySelector('.sidebar-menu');

    // 从后端获取菜单数据
    fetch('/api/menu')
        .then(response => response.json())
        .then(data => {
            // 动态生成菜单
            generateMenu(data);
        })
        .catch(error => {
            console.error("Error fetching menu data:", error);
        });

    // 生成菜单
    function generateMenu(menuData) {
        menuData.forEach(menuItem => {
            const menuLi = document.createElement('li');
            menuLi.classList.add('menu-item');

            // 主菜单项
            const menuLink = document.createElement('a');
            menuLink.href = menuItem.link;
            menuLink.innerHTML = `<i class="bi ${menuItem.icon}"></i><span class="menu-text">${menuItem.title}</span>`;
            menuLi.appendChild(menuLink);

            // 子菜单
            if (menuItem.sub_menu && menuItem.sub_menu.length > 0) {
                const submenuUl = document.createElement('ul');
                submenuUl.classList.add('submenu');
                
                menuItem.sub_menu.forEach(subItem => {
                    const subMenuLi = document.createElement('li');
                    const subMenuLink = document.createElement('a');
                    subMenuLink.href = subItem.link;
                    subMenuLink.innerHTML = `<i class="bi ${subItem.icon}"></i><span class="menu-text">${subItem.title}</span>`;
                    subMenuLi.appendChild(subMenuLink);
                    submenuUl.appendChild(subMenuLi);
                });

                menuLi.appendChild(submenuUl);
            }

            sidebarMenu.appendChild(menuLi);
        });
    }
});
