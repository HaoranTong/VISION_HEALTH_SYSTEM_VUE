// 文件名称：index.js
// 完整保存路径：miniprogram/pages/index/index.js
// 功能说明：首页逻辑控制
// 使用说明：处理页面跳转和初始化逻辑

Page({
  /**
   * 页面初始化事件
   */
  onLoad() {
    console.log('首页加载完成');
  },

  /**
   * 跳转到数据查询页
   */
  navigateToQuery() {
    wx.navigateTo({
      url: '/pages/query/query'
    });
  },

  /**
   * 跳转到数据上传页
   */
  navigateToUpload() {
    wx.navigateTo({
      url: '/pages/upload/upload'
    });
  }
});