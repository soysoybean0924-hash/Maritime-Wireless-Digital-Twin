# Maritime Wireless Digital Twin

Maritime-Wireless-Digital-Twin 是一个面向海陆/海面无线通信场景的数字孪生科研原型。项目聚焦岸边基站、海面移动船舶、通信浮标、无线传播环境与链路质量之间的动态关系，用于展示海上无线覆盖、传播参数变化和实时通信指标。

## 研究对象

本项目研究海陆/海面无线通信场景中的网络覆盖与链路状态，重点关注：

- 岸边基站对近海和远海船舶的无线覆盖能力。
- 海面反射、两径传播、雨雾、海况、风速、温湿压等环境因素对链路预算的影响。
- 蒸发波导/大气波导对横向水平覆盖距离的增强作用，以及覆盖突变时的告警提示。
- 岸基网络、海上中继与低轨卫星备份之间的通信保障关系。

## 主要功能

- 基于 Three.js 的三维海陆通信场景可视化。
- 海面、岸线、基站、船舶、浮标、航迹和通信链路展示。
- 传播参数调节，包括频段、发射功率、天线高度、海况、气象和蒸发波导相关参数。
- 实时指标展示，包括通信距离、路径损耗、接收功率、SNR、链路余量、丢包率和估计吞吐量。
- 异常/事故场景提示，包括基站故障、突发天气、中继异常、船舶天线姿态异常和低轨卫星备份建议。

## 当前运行方法

当前项目是静态 HTML 原型，Three.js 通过 CDN import map 加载。

推荐使用本地静态服务器运行，避免浏览器对 ES module 或本地资源加载的限制：

```powershell
cd D:\GitHubProjects\Maritime-Wireless-Digital-Twin
python -m http.server 8000
```

然后在浏览器打开：

```text
http://localhost:8000/maritime-wireless-digital.html
```

也可以直接打开 HTML 文件进行查看；若浏览器限制模块加载，请改用本地服务器方式。

## 目录说明

```text
.
├── maritime-wireless-digital.html                         # 当前主入口原型，包含告警与低轨卫星备份提示
├── maritime-wireless-digital - 0720添加警示.html           # 添加异常/事故警示后的阶段版本
├── maritime-wireless-digital - 添加低轨卫星版本.html        # 添加低轨卫星备份逻辑的阶段版本
├── maritime-wireless-digital - 0716未添加警示.html          # 早期页面版本
├── Threejs海陆通信场景仿真.html                            # Three.js 海陆通信场景仿真版本
├── Threejs海陆通信场景仿真 - 0716未添加警示.html             # Three.js 早期备份版本
├── 海陆通信场景.html                                       # 早期中文场景页面
├── 添加海面图片maritime-wireless-digital-twin.html          # 添加海面图片后的阶段版本
├── maritime-wireless-digital-twin-presentation-guide.md    # 项目展示与汇报说明
├── 射线轨迹图.png                                          # 传播/射线轨迹示意图
└── v1.pdf                                                  # 项目相关参考或阶段材料
```

## 开发约定

从首次初始化后，本项目唯一开发目录为：

```text
D:\GitHubProjects\Maritime-Wireless-Digital-Twin
```

桌面源目录 `C:\Users\sypxx\Desktop\海陆通信场景` 仅作为原始备份保留，不再继续修改。