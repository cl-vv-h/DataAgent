//index.js
Page({
  data: {
    markets: ['上海', '深圳'],
    marketIndex: 0,
    ticker: '',
    analysisResults: [],
    isLoading: false,
    error: ''
  },

  onLoad() {
    // 页面加载时的初始化
  },

  // 市场选择改变
  onMarketChange(e) {
    this.setData({
      marketIndex: e.detail.value
    })
  },

  // 股票代码输入
  onTickerInput(e) {
    this.setData({
      ticker: e.detail.value
    })
  },

  // 提交查询
  onSubmit() {
    if (!this.data.ticker || this.data.ticker.length !== 6) {
      wx.showToast({
        title: '请输入6位股票代码',
        icon: 'none'
      })
      return
    }

    this.setData({
      isLoading: true,
      error: '',
      analysisResults: []
    })

    // 调用后端API
    this.callAnalysisAPI()
  },

  // 调用分析API
  callAnalysisAPI() {
    const market = this.data.markets[this.data.marketIndex]
    const ticker = this.data.ticker

    wx.request({
      url: 'http://localhost:8000/api/analyze', // 根据你的后端地址调整
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: {
        market: market,
        ticker: ticker
      },
      success: (res) => {
        console.log('API响应:', res.data)
        
        if (res.statusCode === 200 && res.data) {
          // 假设后端返回的是数组格式
          let results = res.data
          if (!Array.isArray(results)) {
            results = [results] // 如果返回单个对象，转换为数组
          }
          
          this.setData({
            analysisResults: results,
            isLoading: false
          })
        } else {
          this.setData({
            error: 'API调用失败',
            isLoading: false
          })
        }
      },
      fail: (err) => {
        console.error('API调用失败:', err)
        this.setData({
          error: '网络请求失败，请检查网络连接',
          isLoading: false
        })
      }
    })
  },

  // 刷新数据
  onRefresh() {
    if (this.data.ticker) {
      this.onSubmit()
    }
  }
})

