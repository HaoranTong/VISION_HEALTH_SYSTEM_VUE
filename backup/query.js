/**
 * 文件名称：query.js
 * 完整存储路径：frontend/static/js/query.js
 * 功能说明：
 *    实现数据查询页面的前端逻辑，包括：
 *      - 收集查询条件（教育ID号、学校、年级、班级、数据年份、姓名、性别、身份证号码）。
 *      - 发送 GET 请求到后端查询 API (/api/students/query)，支持分页与导出Excel功能。
 *      - 根据返回数据渲染查询结果表格及分页按钮。
 *      - 处理列配置下拉框，允许用户通过复选框选择哪些列在表格中显示。
 *      - “清除”按钮用于清空所有查询条件输入框。
 * 使用说明：
 *    1. 确保在 query.html 中已定义相应的 DOM 元素（查询条件输入框、按钮、表格、分页等）。
 *    2. 该脚本在页面加载后自动执行，并在用户操作时动态更新页面内容。
 * 详细注释已在代码中给出。
 */

document.addEventListener('DOMContentLoaded', function() {
  // 获取页面中DOM元素引用
  const searchBtn = document.getElementById('searchBtn');
  const exportBtn = document.getElementById('exportBtn');
  const clearBtn = document.getElementById('clearBtn');
  const resultTableBody = document.getElementById('resultTableBody');
  const pagination = document.getElementById('pagination');
  const selectAllCheckbox = document.getElementById('selectAllColumns');
  const columnCheckboxes = document.querySelectorAll('.column-checkbox');

  let currentPage = 1;
  let perPage = 10;

  /**
   * fetchData 函数用于发送查询请求，并根据参数决定是否导出数据
   * @param {boolean} exportFlag - 若为 true，则执行导出功能，否则为普通查询
   */
  function fetchData(exportFlag = false) {
    const params = new URLSearchParams();
    // 从页面输入框获取查询条件
    const educationId = document.getElementById('education_id').value.trim();
    const school = document.getElementById('school').value.trim();
    const grade = document.getElementById('grade').value.trim();
    const className = document.getElementById('class_name').value.trim();
    const dataYear = document.getElementById('data_year').value.trim(); // 获取数据年份
    const name = document.getElementById('name').value.trim();
    const gender = document.getElementById('gender').value.trim();
    const idCard = document.getElementById('id_card').value.trim();

    // 将非空查询条件添加到URL参数中
    if (educationId) params.append('education_id', educationId);
    if (school) params.append('school', school);
    if (grade) params.append('grade', grade);
    if (className) params.append('班级', className);
    if (dataYear) params.append('data_year', dataYear);
    if (name) params.append('name', name);
    if (gender) params.append('gender', gender);
    if (idCard) params.append('id_card', idCard);

    // 分页参数或导出标志
    if (!exportFlag) {
      params.append('page', currentPage);
      params.append('per_page', perPage);
    } else {
      params.append('export', '1');
    }

    // 发送 GET 请求到查询API
    fetch(`/api/students/query?${params.toString()}`)
      .then(response => {
        if (exportFlag) {
          return response.blob();
        }
        return response.json();
      })
      .then(function(data) {
        if (exportFlag) {
          // 导出功能：创建下载链接并自动点击
          const url = window.URL.createObjectURL(data);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = url;
          a.download = 'students_export.xlsx';
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
        } else {
          // 渲染查询结果表格
          resultTableBody.innerHTML = '';
          data.students.forEach(function(student) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td data-column="education_id">${student.education_id || ''}</td>
              <td data-column="school">${student.school || ''}</td>
              <td data-column="grade">${student.grade || ''}</td>
              <td data-column="class_name">${student.class_name || ''}</td>
              <td data-column="height">${student.height !== undefined ? student.height : ''}</td>
              <td data-column="weight">${student.weight !== undefined ? student.weight : ''}</td>
              <td data-column="name">${student.name || ''}</td>
              <td data-column="gender">${student.gender || ''}</td>
              <td data-column="age">${student.age !== undefined ? student.age : ''}</td>
              <td data-column="birthday">${student.birthday || ''}</td>
              <td data-column="phone">${student.phone || ''}</td>
              <td data-column="id_card">${student.id_card || ''}</td>
              <td data-column="region">${student.region || ''}</td>
              <td data-column="contact_address">${student.contact_address || ''}</td>
              <td data-column="parent_name">${student.parent_name || ''}</td>
              <td data-column="parent_phone">${student.parent_phone || ''}</td>
              <td data-column="data_year">${student.data_year || ''}</td>
              <td data-column="diet_preference">${student.diet_preference || ''}</td>
              <td data-column="exercise_preference">${student.exercise_preference || ''}</td>
              <td data-column="health_education">${student.health_education || ''}</td>
              <td data-column="past_history">${student.past_history || ''}</td>
              <td data-column="family_history">${student.family_history || ''}</td>
              <td data-column="premature">${student.premature || ''}</td>
              <td data-column="allergy">${student.allergy || ''}</td>
              <td data-column="frame_glasses">${student.frame_glasses !== undefined ? student.frame_glasses : ''}</td>
              <td data-column="contact_lenses">${student.contact_lenses !== undefined ? student.contact_lenses : ''}</td>
              <td data-column="night_orthokeratology">${student.night_orthokeratology !== undefined ? student.night_orthokeratology : ''}</td>
              <td data-column="guasha">${student.guasha !== undefined ? student.guasha : ''}</td>
              <td data-column="aigiu">${student.aigiu !== undefined ? student.aigiu : ''}</td>
              <td data-column="zhongyao_xunzheng">${student.zhongyao_xunzheng !== undefined ? student.zhongyao_xunzheng : ''}</td>
              <td data-column="rejiu_training">${student.rejiu_training !== undefined ? student.rejiu_training : ''}</td>
              <td data-column="xuewei_tiefu">${student.xuewei_tiefu !== undefined ? student.xuewei_tiefu : ''}</td>
              <td data-column="reci_pulse">${student.reci_pulse !== undefined ? student.reci_pulse : ''}</td>
              <td data-column="baoguan">${student.baoguan !== undefined ? student.baoguan : ''}</td>
              <td data-column="right_eye_naked">${student.right_eye_naked !== undefined ? student.right_eye_naked : ''}</td>
              <td data-column="left_eye_naked">${student.left_eye_naked !== undefined ? student.left_eye_naked : ''}</td>
              <td data-column="right_eye_corrected">${student.right_eye_corrected !== undefined ? student.right_eye_corrected : ''}</td>
              <td data-column="left_eye_corrected">${student.left_eye_corrected !== undefined ? student.left_eye_corrected : ''}</td>
              <td data-column="right_sphere">${student.right_sphere !== undefined ? student.right_sphere : ''}</td>
              <td data-column="right_cylinder">${student.right_cylinder !== undefined ? student.right_cylinder : ''}</td>
              <td data-column="right_axis">${student.right_axis !== undefined ? student.right_axis : ''}</td>
              <td data-column="left_sphere">${student.left_sphere !== undefined ? student.left_sphere : ''}</td>
              <td data-column="left_cylinder">${student.left_cylinder !== undefined ? student.left_cylinder : ''}</td>
              <td data-column="left_axis">${student.left_axis !== undefined ? student.left_axis : ''}</td>
              <td data-column="eye_fatigue">${student.eye_fatigue || ''}</td>
              <td data-column="right_eye_naked_interv">${student.right_eye_naked_interv !== undefined ? student.right_eye_naked_interv : ''}</td>
              <td data-column="left_eye_naked_interv">${student.left_eye_naked_interv !== undefined ? student.left_eye_naked_interv : ''}</td>
              <td data-column="right_sphere_interv">${student.right_sphere_interv !== undefined ? student.right_sphere_interv : ''}</td>
              <td data-column="right_cylinder_interv">${student.right_cylinder_interv !== undefined ? student.right_cylinder_interv : ''}</td>
              <td data-column="right_axis_interv">${student.right_axis_interv !== undefined ? student.right_axis_interv : ''}</td>
              <td data-column="left_sphere_interv">${student.left_sphere_interv !== undefined ? student.left_sphere_interv : ''}</td>
              <td data-column="left_cylinder_interv">${student.left_cylinder_interv !== undefined ? student.left_cylinder_interv : ''}</td>
              <td data-column="left_axis_interv">${student.left_axis_interv !== undefined ? student.left_axis_interv : ''}</td>
            `;
            // 点击行跳转到学生详情页
            tr.addEventListener('click', function() {
              window.location.href = `/student_detail?id=${student.id}`;
            });
            resultTableBody.appendChild(tr);
          });
          // 分页处理：动态生成分页按钮
          pagination.innerHTML = '';
          const totalPages = Math.ceil(data.total / perPage);
          for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement('li');
            li.className = 'page-item' + (i === currentPage ? ' active' : '');
            li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            li.addEventListener('click', function(e) {
              e.preventDefault();
              currentPage = i;
              fetchData();
            });
            pagination.appendChild(li);
          }
          // 根据列配置更新表格显示（仅隐藏未选中的列）
          updateTableColumns();
        }
      })
      .catch(function(err) {
        console.error('查询错误:', err);
      });
  }

  /**
   * updateTableColumns 根据列配置下拉框的选中状态更新表格列的显示/隐藏
   */
  function updateTableColumns() {
    const selectedColumns = Array.from(columnCheckboxes)
      .filter(cb => cb.checked)
      .map(cb => cb.value);
    const table = document.getElementById('resultsTable');
    if (!table) return;
    // 更新表头列显示
    const ths = table.querySelectorAll('th');
    ths.forEach(th => {
      if (selectedColumns.includes(th.getAttribute('data-column'))) {
        th.style.display = '';
      } else {
        th.style.display = 'none';
      }
    });
    // 更新表格单元格显示
    const trs = table.querySelectorAll('tbody tr');
    trs.forEach(tr => {
      const tds = tr.querySelectorAll('td');
      tds.forEach(td => {
        if (selectedColumns.includes(td.getAttribute('data-column'))) {
          td.style.display = '';
        } else {
          td.style.display = 'none';
        }
      });
    });
  }

  // 全选/取消复选框事件绑定
  selectAllCheckbox.addEventListener('change', function() {
    columnCheckboxes.forEach(function(cb) {
      cb.checked = selectAllCheckbox.checked;
    });
    updateTableColumns();
  });

  // 单个复选框变化事件绑定
  columnCheckboxes.forEach(function(cb) {
    cb.addEventListener('change', function() {
      updateTableColumns();
    });
  });

  // 清除按钮：清空所有查询条件输入框
  clearBtn.addEventListener('click', function() {
    document.getElementById('education_id').value = '';
    document.getElementById('school').value = '';
    document.getElementById('grade').value = '';
    document.getElementById('class_name').value = '';
    document.getElementById('data_year').value = '';
    document.getElementById('name').value = '';
    document.getElementById('gender').value = '';
    document.getElementById('id_card').value = '';
  });

  // 按钮事件绑定：查询和导出
  searchBtn.addEventListener('click', function() {
    currentPage = 1; // 重置页码
    fetchData();
  });

  exportBtn.addEventListener('click', function() {
    fetchData(true);
  });

  // 页面加载时，初始加载查询数据
  fetchData();
});
