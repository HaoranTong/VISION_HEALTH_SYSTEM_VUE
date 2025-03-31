// 文件名称：auth.js
// 完整保存路径：miniprogram/utils/auth.js
// 功能说明：微信登录认证模块
// 使用说明：通过wx.login获取code，调用后端接口完成登录

/**
 * 微信登录函数
 * @returns {Promise<string>} 返回用户的唯一标识openid
 */
export const wechatLogin = () => {
  return new Promise((resolve, reject) => {
    wx.login({
      success: async (res) => {
        if (res.code) {
          try {
            // 调用后端登录接口
            const response = await wx.request({
              url: `${getApp().globalData.apiBaseUrl}/auth/login`,
              method: 'POST',
              data: { code: res.code }
            });
            resolve(response.data.openid);
          } catch (error) {
            reject(new Error('登录失败：' + error.message));
          }
        } else {
          reject(new Error('获取登录凭证失败'));
        }
      }
    });
  });
};