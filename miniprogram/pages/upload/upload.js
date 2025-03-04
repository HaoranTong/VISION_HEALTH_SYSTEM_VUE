// 文件名称：upload.js
// 完整保存路径：miniprogram/pages/upload/upload.js
// 功能说明：数据上传页逻辑控制
// 使用说明：处理文字输入、图片上传和表单提交

Page({
  data: {
    text: '',        // 文字输入内容
    images: []       // 上传的图片临时路径
  },

  /**
   * 文字输入事件处理
   */
  onInputText(e) {
    this.setData({ text: e.detail.value });
  },

  /**
   * 选择图片
   */
  chooseImage() {
    wx.chooseImage({
      count: 3, // 最多选择3张图片
      success: (res) => {
        this.setData({ images: this.data.images.concat(res.tempFilePaths) });
      }
    });
  },

  /**
   * 删除图片
   */
  deleteImage(e) {
    const index = e.currentTarget.dataset.index;
    const images = this.data.images.filter((_, i) => i !== index);
    this.setData({ images });
  },

  /**
   * 提交表单
   */
  async submit() {
    const { text, images } = this.data;
    if (!text.trim()) {
      wx.showToast({ title: '请输入干预描述', icon: 'none' });
      return;
    }

    // 调用后端接口
    try {
      const res = await wx.request({
        url: `${getApp().globalData.apiBaseUrl}/students/import`,
        method: 'POST',
        header: { 'Content-Type': 'multipart/form-data' },
        data: { 
          description: text,
          images: images.map(path => ({ name: 'file', uri: path }))
        }
      });
      
      if (res.statusCode === 200) {
        wx.showToast({ title: '上传成功' });
        this.setData({ text: '', images: [] });
      } else {
        throw new Error(res.data.error || '上传失败');
      }
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'none' });
    }
  }
});