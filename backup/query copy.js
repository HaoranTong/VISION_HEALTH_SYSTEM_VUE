// 文件名称：query.js
// 完整路径：frontend/static/js/query.js
// 功能说明：完整数据查询逻辑（已修复显示问题）

document.addEventListener('DOMContentLoaded', function() {
  // 获取页面元素
  const searchBtn = document.getElementById('searchBtn');
  const exportBtn = document.getElementById('exportBtn');
  const clearBtn = document.getElementById('clearBtn');
  const resultTableBody = document.getElementById('resultTableBody');
  const pagination = document.getElementById('pagination');
  const selectAllCheckbox = document.getElementById('selectAllColumns');
  const columnCheckboxes = document.querySelectorAll('.column-checkbox');

  // 初始化配置
  let currentPage = 1;
  let perPage = 10;

  // ================== 新增代码块（开始）==================
  // 1. 设置默认显示列
  const defaultColumns = [
    'data_year','school','grade','class_name','name','gender',
    'left_eye_naked','right_eye_naked',
    'left_eye_naked_interv','right_eye_naked_interv'
  ];
  
  // 自动勾选默认列
  document.querySelectorAll('.column-checkbox').forEach(cb => {
    cb.checked = defaultColumns.includes(cb.value);
  });
  // ================== 新增代码块（结束）==================

  // 查询数据主函数
  function fetchData(exportFlag = false) {
    const params = new URLSearchParams();
    
    // 收集查询条件（所有输入框）
    const educationId = document.getElementById('education_id').value.trim();
    const school = document.getElementById('school').value.trim();
    const grade = document.getElementById('grade').value.trim();
    const className = document.getElementById('class_name').value.trim();
    const dataYear = document.getElementById('data_year').value.trim();
    const name = document.getElementById('name').value.trim();
    const gender = document.getElementById('gender').value.trim();
    const idCard = document.getElementById('id_card').value.trim();

    // 设置查询参数
    if(educationId) params.append('education_id', educationId);
    if(school) params.append('school', school);
    if(grade) params.append('grade', grade);
    if(className) params.append('班级', className);
    if(dataYear) params.append('data_year', dataYear);
    if(name) params.append('name', name);
    if(gender) params.append('gender', gender);
    if(idCard) params.append('id_card', idCard);

    // 分页参数
    if(!exportFlag){
      params.append('page', currentPage);
      params.append('per_page', perPage);
    }else{
      params.append('export', '1');
    }

    // 发送请求
    fetch(`/api/students/query?${params.toString()}`)
      .then(response => {
        if(exportFlag) return response.blob();
        return response.json();
      })
      .then(function(data){
        if(exportFlag){
          // 导出处理（保持不变）
          const url = window.URL.createObjectURL(data);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = url;
          a.download = 'students_export.xlsx';
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
        }else{
          // ================== 修改代码块（开始）==================
          // 清空现有数据
          resultTableBody.innerHTML = '';
          
          // 渲染新数据
          data.students.forEach(function(student) {
            const tr = document.createElement('tr');
            // 自动处理空值显示
            tr.innerHTML = `
              <td>${student.education_id || ''}</td>
              <td>${student.school || ''}</td>
              <td>${student.grade || ''}</td>
              <td>${student.class_name || ''}</td>
              <td>${student.name || ''}</td>
              <td>${student.gender || ''}</td>
              <td>${student.left_eye_naked || ''}</td>
              <td>${student.right_eye_naked || ''}</td>
              <td>${student.left_eye_naked_interv || ''}</td>
              <td>${student.right_eye_naked_interv || ''}</td>
            `;
            resultTableBody.appendChild(tr);
          });
          // ================== 修改代码块（结束）==================
          
          // 更新分页（保持不变）
          pagination.innerHTML = '';
          const totalPages = Math.ceil(data.total / perPage);
          for(let i=1; i<=totalPages; i++){
            const li = document.createElement('li');
            li.className = 'page-item' + (i===currentPage ? ' active' : '');
            li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            li.addEventListener('click', function(e){
              e.preventDefault();
              currentPage = i;
              fetchData();
            });
            pagination.appendChild(li);
          }
        }
      })
      .catch(function(err){
        console.error('查询错误:', err);
      });
  }

  // 其他功能（全选/清除等，保持不变）
  selectAllCheckbox.addEventListener('change', function(){
    columnCheckboxes.forEach(function(cb){
      cb.checked = selectAllCheckbox.checked;
    });
    updateTableColumns();
  });

  columnCheckboxes.forEach(function(cb){
    cb.addEventListener('change', function(){
      updateTableColumns();
    });
  });

  clearBtn.addEventListener('click', function(){
    document.getElementById('education_id').value = '';
    document.getElementById('school').value = '';
    document.getElementById('grade').value = '';
    document.getElementById('class_name').value = '';
    document.getElementById('data_year').value = '';
    document.getElementById('name').value = '';
    document.getElementById('gender').value = '';
    document.getElementById('id_card').value = '';
  });

  searchBtn.addEventListener('click', function(){
    currentPage = 1;
    fetchData();
  });

  exportBtn.addEventListener('click', function(){
    fetchData(true);
  });

  // 初始化加载
  fetchData();
});

// 列显示控制（新增函数）
function updateTableColumns(){
  const selectedColumns = Array.from(document.querySelectorAll('.column-checkbox'))
    .filter(cb => cb.checked)
    .map(cb => cb.value);

  // 控制表头显示
  document.querySelectorAll('th').forEach(th => {
    th.style.display = selectedColumns.includes(th.dataset.column) ? '' : 'none';
  });

  // 控制表格内容显示
  document.querySelectorAll('td').forEach(td => {
    td.style.display = selectedColumns.includes(td.dataset.column) ? '' : 'none';
  });
}