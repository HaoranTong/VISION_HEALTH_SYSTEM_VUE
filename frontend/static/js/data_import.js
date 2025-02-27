/* 
文件名称: data_import.js
完整存储路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\frontend\static\js\data_import.js
功能说明:
    该文件处理数据导入页面的所有交互，包括选择文件、拖拽文件、显示文件列表、上传文件、显示上传状态和处理文件删除等。
使用方法:
    加载页面时，页面元素会自动绑定相关的事件，包括文件选择、文件上传等交互功能。
*/
document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('fileInput');
  const selectFileBtn = document.getElementById('selectFileBtn');
  const cancelBtn = document.getElementById('cancelBtn');
  const uploadBtn = document.getElementById('uploadBtn');
  const fileList = document.getElementById('fileList');
  const uploadArea = document.getElementById('uploadArea');
  const uploadStatus = document.getElementById('uploadStatus');
  const dataYearSelect = document.getElementById('dataYearSelect');

  // 存储选择的文件（数组）
  let selectedFiles = [];

  // 更新显示选中文件列表
  function updateFileList() {
    if (selectedFiles.length === 0) {
      fileList.innerHTML = '<p class="text-muted">暂无选中文件</p>';
      return;
    }
    fileList.innerHTML = '';
    selectedFiles.forEach((file, index) => {
      const fileItem = document.createElement('div');
      fileItem.style.display = 'flex';
      fileItem.style.justifyContent = 'space-between';
      fileItem.style.alignItems = 'center';
      fileItem.style.padding = '6px 0';
      fileItem.style.borderBottom = '1px solid #eee';
      fileItem.innerHTML = `
        <span>${file.name}</span>
        <button type="button" class="btn btn-sm btn-link text-danger" data-index="${index}">
          <i class="bi bi-x-circle"></i>
        </button>`;
      fileList.appendChild(fileItem);
    });
  }

  // 选择文件按钮点击
  selectFileBtn.addEventListener('click', () => {
    fileInput.click();  // 触发文件选择框
  });

  // 文件输入改变时更新文件列表
  fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    selectedFiles = selectedFiles.concat(files);
    updateFileList();
  });

  // 处理拖拽文件
  uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.backgroundColor = '#f7f7f7';
  });

  uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.style.backgroundColor = '';
  });

  uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.backgroundColor = '';
    const files = Array.from(e.dataTransfer.files).filter(file => {
      const ext = file.name.split('.').pop().toLowerCase();
      return ext === 'xlsx' || ext === 'csv';
    });
    selectedFiles = selectedFiles.concat(files);
    updateFileList();
  });

  // 点击取消上传按钮，清空选中文件
  cancelBtn.addEventListener('click', () => {
    selectedFiles = [];
    fileInput.value = '';
    updateFileList();
    uploadStatus.innerHTML = '<div class="alert alert-info mt-2">已取消所有选择的文件。</div>';
  });

  // 绑定删除单个文件事件（通过委托方式绑定）
  fileList.addEventListener('click', (e) => {
    if (e.target.closest('button')) {
      const index = e.target.closest('button').getAttribute('data-index');
      selectedFiles.splice(index, 1);
      updateFileList();
    }
  });

  // 上传文件按钮点击
  uploadBtn.addEventListener('click', () => {
    if (selectedFiles.length === 0) {
      uploadStatus.innerHTML = '<div class="alert alert-warning mt-2">请选择要上传的文件。</div>';
      return;
    }
    const dataYear = dataYearSelect.value;
    const formData = new FormData();
    formData.append('data_year', dataYear);
    selectedFiles.forEach(file => {
      formData.append('file', file);
    });
    uploadStatus.innerHTML = '<div class="alert alert-info mt-2">正在上传，请稍候……</div>';
    fetch("/api/students/import", {  // 修改：直接使用硬编码的 URL
      method: 'POST',
      body: formData
    })
      .then(response => response.json())
      .then(result => {
        if (result.error) {
          uploadStatus.innerHTML = `<div class="alert alert-danger mt-2">${result.error}</div>`;
        } else {
          uploadStatus.innerHTML = `<div class="alert alert-success mt-2">${result.message}</div>`;
        }
      })
      .catch(err => {
        uploadStatus.innerHTML = `<div class="alert alert-danger mt-2">上传过程中出现错误：${err}</div>`;
        console.error('上传错误:', err);
      });
  });
});