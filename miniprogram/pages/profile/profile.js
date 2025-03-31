// 文件名称：profile.js
// 完整保存路径：miniprogram/pages/profile/profile.js
// 功能说明：个人中心页逻辑控制
// 使用说明：加载和更新用户信息

Page({
  data: {
    userInfo: {
      avatarUrl: '',   // 用户头像
      nickName: '未登录', // 微信昵称
      name: '',         // 真实姓名
      phone: ''         // 联系电话
    }
  },

  /**
   * 页面加载时获取用户信息
   */
  onLoad() {
    this.loadUserInfo();
  },

  /**
   * 加载用户信息
   */
  async loadUserInfo() {
    const { userInfo } = await wx.getUserProfile({ desc: '用于展示个人信息' });
    this.setData({ userInfo: { ...userInfo, ...this.data.userInfo } });
  },

  /**
   * 输入事件处理
   */
  onNameInput(e) {
    this.setData({ 'userInfo.name': e.detail.value });
  },
  onPhoneInput(e) {
    this.setData({ 'userInfo.phone': e.detail.value });
  },

  /**
   * 保存修改
   */
  async saveProfile() {
    const { userInfo } = this.data;
    try {
      const res = await wx.request({
        url: `${getApp().globalData.apiBaseUrl}/student/add`,
        method: 'POST',
        data: userInfo
      });
      if (res.statusCode === 201) {
        wx.showToast({ title: '保存成功' });
      }
    } catch (error) {
      wx.showToast({ title: '保存失败', icon: 'none' });
    }
  }
});