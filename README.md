# ☕ coffeegirl Trading Bot

**智能交易 · 风险控制 · 稳定收益**

一个基于链上数据和技术分析的自动化交易机器人，专为加密货币交易比赛设计。

## 🚀 特性

### 核心策略
- **4小时趋势分析** - 结合EMA指标识别市场趋势
- **链上数据集成** - 使用Horus API获取鲸鱼行为和矿工活动数据
- **多因子决策** - 技术指标与链上信号的智能融合

### 风险控制
- **动态仓位管理** - 基于信心度的智能仓位调整
- **严格止损止盈** - 1.2%止盈，2.5%止损
- **交易频率限制** - 防止过度交易，符合比赛规则
- **时间止损机制** - 最长持仓时间控制

### 技术特点
- **完全自动化** - 无需人工干预
- **实时监控** - 每30秒执行交易周期
- **异常处理** - 完善的错误处理和日志记录
- **模拟平台适配** - 针对Roostoo平台的优化

## 📁 项目结构
coffeegirl-trading-bot/
├── main.py # 主程序入口
├── config.py # 配置文件
├── exchange_api.py # 交易所API接口
├── strategy_engine.py # 策略引擎核心
├── technical_analyzer.py # 技术分析模块
├── risk_manager.py # 风险管理模块
├── portfolio_manager.py # 投资组合管理
└── requirements.txt # Python依赖

text

## ⚙️ 配置参数

### 交易设置
```python
SYMBOLS = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", "BNBUSDT"]
EXECUTION_INTERVAL = 30  # 执行间隔(秒)
MAX_TRADES_PER_DAY = 50  # 每日最大交易次数
风险参数

python
MAX_PORTFOLIO_RISK = 0.025    # 组合最大风险
MAX_POSITION_SIZE = 0.20      # 单笔最大仓位
STOP_LOSS_PCT = 0.025         # 止损比例
TAKE_PROFIT_PCT = 0.012       # 止盈比例
🛠️ 安装和运行

环境要求
Python 3.8+
Roostoo交易账户
Horus API密钥
安装步骤

克隆仓库
bash
git clone <repository-url>
cd coffeegirl-trading-bot
安装依赖
bash
pip install -r requirements.txt
配置环境变量
bash
cp .env.example .env
# 编辑 .env 文件，添加API密钥
运行机器人
bash
python3 main.py
📊 策略逻辑

买入信号

趋势确认 - EMA50 > EMA100，价格在EMA50上方
链上支持 - 鲸鱼净流入，矿工无压力
信心度达标 - 综合信心度 > 0.6
卖出信号

止盈触发 - 收益达到1.2%
止损触发 - 亏损达到2.5%
时间止损 - 持仓超过最大时间
🔧 核心模块

StrategyEngine

集成技术分析和链上数据
生成交易信号和执行决策
管理交易生命周期
RiskManager

实时风险监控
交易审批和限制
性能指标追踪
PortfolioManager

投资组合状态管理
仓位跟踪和更新
现金和资产平衡
📈 监控指标

机器人运行时显示：

✅ 交易状态和操作
💰 投资组合总值和现金余额
📊 持仓数量和胜率
📉 当前回撤和交易统计
🎯 比赛合规性

✅ 完全自动化，无人工干预
✅ 禁止高频交易（每30秒执行）
✅ 仅现货交易，无杠杆做空
✅ 开源代码提交
✅ AWS EC2部署
🤝 团队信息

📄 许可证

本项目仅用于比赛目的，请遵守相关平台的使用条款。

喝杯咖啡，让机器人帮你交易！☕
