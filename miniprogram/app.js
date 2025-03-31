// 文件名称：app.js
// 完整保存路径：miniprogram/app.js
// 功能说明：小程序入口文件，初始化全局数据和生命周期
// 使用说明：此文件由小程序自动加载，无需手动调用

App({
  onLaunch() {
    // 小程序初始化时执行
    console.log('小程序初始化完成');
  },
  globalData: {
    userInfo: null,     // 全局用户信息
    apiBaseUrl: 'https://your-api-domain.com/api' // 后端API基础地址
  }
});