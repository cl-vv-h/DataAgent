# 股票分析助手 - 微信小程序

这是一个用于股票分析的微信小程序前端项目，可以查询股票的分析结果并展示多个分析框体。

## 功能特性

- 🏢 支持上海和深圳两个市场选择
- 📊 输入6位股票代码进行查询
- 📈 展示多个分析结果框体
- 🎨 美观的UI设计和响应式布局
- ⚡ 实时API调用和结果展示

## 项目结构

```
frontend/
├── app.js                 # 小程序主文件
├── app.json              # 小程序配置文件
├── app.wxss              # 全局样式文件
├── project.config.json   # 项目配置文件
├── sitemap.json          # 站点地图配置
├── pages/                # 页面目录
│   └── index/           # 主页面
│       ├── index.wxml   # 页面结构
│       ├── index.js     # 页面逻辑
│       └── index.wxss   # 页面样式
└── README.md             # 项目说明
```

## 使用方法

1. **市场选择**: 点击下拉选择器选择"上海"或"深圳"市场
2. **股票代码输入**: 在输入框中输入6位股票代码
3. **查询分析**: 点击"查询分析"按钮提交请求
4. **查看结果**: 系统会显示多个分析结果框体，每个框体包含：
   - 整体信号（看涨/看跌）
   - 置信度
   - DCF分析结果
   - 所有者收益分析结果

## 后端API配置

小程序会调用后端API获取分析数据，默认API地址为：
```
http://localhost:8000/api/analyze
```

API请求格式：
```json
{
  "market": "上海",  // 或 "深圳"
  "ticker": "000001"  // 6位股票代码
}
```

API响应格式（参考res5.json）：
```json
{
  "signal": "看跌",
  "confidence": "100%",
  "reasoning": {
    "dcf_analysis": {
      "signal": "看跌",
      "reasoning": "实际dcf值: $0.00, 市值: $15,254,297,463.00, Gap: -100.0%"
    },
    "owner_earnings_analysis": {
      "signal": "看跌",
      "reasoning": "Owner Earnings Value: $0.00, 市值: $15,254,297,463.00, Gap: -100.0%"
    }
  }
}
```

## 配置说明

### 1. 修改API地址
在 `pages/index/index.js` 文件中修改 `callAnalysisAPI` 函数中的URL：
```javascript
url: 'http://your-backend-url/api/analyze'
```

### 2. 修改小程序AppID
在 `project.config.json` 文件中修改 `appid` 字段为你的小程序AppID。

## 开发环境

- 微信开发者工具
- 支持ES6语法
- 使用微信小程序原生框架

## 部署说明

1. 在微信开发者工具中导入项目
2. 修改 `project.config.json` 中的AppID
3. 配置后端API地址
4. 预览和调试
5. 上传代码到微信小程序后台

## 注意事项

- 确保后端API正常运行并可访问
- 股票代码必须是6位数字
- 网络请求失败时会显示错误提示
- 支持多个分析结果的展示

## 技术支持

如有问题，请检查：
1. 网络连接是否正常
2. 后端API是否正常运行
3. 股票代码格式是否正确
4. 微信开发者工具配置是否正确

