# LLBot

这是去年的时候无聊写的一个可以使用iOS设备，自动玩LoveLive SIF的脚本。

## Usage

**Learning script**
`imgprocess.py`
使用OpenCV学习游戏视频并尝试自行分析谱面信息。
注意请选择视频播放速度较为准确的视频，否则会有很大误差。


**Player script**
`llbot.py [IP Address]`
首先你需要自己魔改SIF的.ipa文件，需要插入`cycript`并自签名。具体过程请自行Google。
请保持iOS设备和电脑在同一网络下面（建议使用USB Tethering。）
打开SIF后执行上述指令，会自动连接至手机。选择歌曲、组队后**不要点击开始**并操作脚本即可。
谱面信息保存在`songdata/`中，已经预加载了一部分谱面（是从游戏中提取的）。
你也可以使用上述学习脚本学习谱面或自行从游戏中提取。
