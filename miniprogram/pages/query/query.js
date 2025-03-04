// 文件名称：query.js
// 完整保存路径：miniprogram/pages/query/query.js
// 功能说明：数据查询页逻辑控制
// 使用说明：调用后端接口获取学生视力数据

const { wechatLogin } = require('../../utils/auth');

Page({
  data: {
    records: [],       // 存储查询结果
    isLoading: false   // 加载状态
  },

  /**
   * 页面加载时自动查询数据
   */
  async onLoad() {
    try {
      this.setData({ isLoading: true });
      const openid = await wechatLogin();
      const response = await wx.request({
        url: `${getApp().globalData.apiBaseUrl}/students/query`,
        method: 'GET',
        data: { openid }
      });
      this.setData({ records: response.data });
    } catch (error) {
      wx.showToast({ title: error.message, icon: 'none' });
    } finally {
      this.setData({ isLoading: false });
    }
  }
});