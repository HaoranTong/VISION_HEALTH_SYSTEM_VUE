// 侧边栏交互逻辑
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('toggleSidebar');

    // 初始化状态
    const savedState = localStorage.getItem('sidebarState');
    if (savedState === 'collapsed') sidebar.classList.add('collapsed');

    // 折叠按钮事件
    toggleBtn.addEventListener('click', () => {
        const isCollapsed = sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebarState', isCollapsed ? 'collapsed' : 'expanded');
    });

    // 子菜单交互
    document.querySelectorAll('.menu-toggle').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const parent = btn.closest('.menu-item');
            const submenu = parent.querySelector('.submenu');
            const arrow = btn.querySelector('.arrow');
            
            // 关闭其他菜单
            document.querySelectorAll('.menu-item').forEach(item => {
                if (item !== parent) {
                    item.classList.remove('active');
                    item.querySelector('.submenu').style.maxHeight = '0';
                    item.querySelector('.arrow').classList.remove('rotate');
                }
            });

            // 切换当前菜单
            parent.classList.toggle('active');
            submenu.style.maxHeight = submenu.style.maxHeight === '0px' ? '500px' : '0';
            arrow.classList.toggle('rotate');
        });
    });
});
