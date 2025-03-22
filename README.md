通用多游戏LLM对战平台需求方案

一、设计目标
跨游戏标准化：支持象棋、围棋、斗地主等回合制/非对称规则游戏的统一接入。

LLM动作抽象：将不同游戏的交互抽象为「状态输入-动作输出」通用范式。

轻量可扩展：新增游戏时仅需实现规则引擎，无需修改核心架构。




三、关键技术决策
前端框架选择

推荐Svelte：适合需要高性能渲染棋类游戏的场景，编译时优化减少运行时开销

备选方案：React + React-Konva（Canvas渲染）

通信优化策略

二进制协议：对棋盘状态数据（如围棋的19x19矩阵）使用MessagePack替代JSON

增量更新：仅传输变化部分（如{"diff": [[x,y], new_value]}）

配音实现方案

方案一：接入TTS服务（如Azure Speech），在服务端生成语音后返回URL

方案二：预录制LLM的常用短语（如"将军！"），根据消息关键词触发播放

四、演进路线图
第一阶段（基础框架）

实现中国象棋、围棋的棋盘渲染与基础规则

完成LLM代理与FastAPI的WebSocket通信

实现基础录屏日志（JSON格式）

第二阶段（扩展能力）

增加斗地主手牌渲染组件

实现TTS语音合成接口

开发回放播放器（时间轴控制）

第三阶段（体验优化）

添加动画效果：棋子移动、打劫标记闪烁

实现LLM思考状态提示（如"Deepseek正在思考..."）

支持导出录屏为GIF/MP4

五、程序文件说明

cyber-ai-games/
├── frontend/                  # 前端代码
│   ├── public/                # 静态资源
│   ├── src/
│   │   ├── components/        # 通用组件
│   │   │   ├── GameSelector   # 游戏选择下拉框
│   │   │   ├── LLMAvatar      # LLM角色选择卡片（含配音图标）
│   │   │   └── ReplayTimeline # 回放进度条
│   │   ├── games/             # 各游戏界面组件
│   │   │   ├── Chess          # 中国象棋
│   │   │   │   ├── Board.svelte # SVG棋盘渲染
│   │   │   │   └── Piece.svelte # 棋子动画
│   │   │   ├── Go             # 围棋
│   │   │   └── DouDiZhu       # 斗地主（手牌渲染组件）
│   │   ├── stores/            # 状态管理
│   │   │   ├── gameStore.ts   # 当前游戏状态
│   │   │   └── chatStore.ts   # 聊天记录
│   │   └── App.svelte         # 主界面布局
├── backend/                   # 后端代码
│   ├── game_engine/           # 通用游戏引擎
│   │   ├── rule_base.py       # 规则基类
│   │   ├── chess_rules.py     # 象棋规则实现
│   │   └── replay_recorder.py # 录屏存储
│   ├── llm_proxy/             # LLM代理服务
│   │   ├── deepseek.py        # DeepSeek接口封装
│   │   └── openai.py          # GPT接口封装
│   └── main.py                # FastAPI入口
└── shared/                    # 前后端共享代码
    └── protocol.py            # WebSocket协议定义