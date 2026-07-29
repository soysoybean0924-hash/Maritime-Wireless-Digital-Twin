# 海陆通信 Three.js 仿真公式说明

本文档对应 `Threejs海陆通信场景仿真 -场景加大版.html` 中当前使用的主要物理、信道和可视化公式。该页面是教学/数字孪生原型可视化：部分公式是工程近似或可视化代理，不等价于完整高保真电磁全波求解。

## 1. 蒸发波导与折射率模型

### 饱和水汽压

代码中用 Magnus 近似计算温度 `T` 下的饱和水汽压：

```text
e_s(T) = 6.112 * exp(17.67 T / (T + 243.5))
```

其中 `T` 单位为摄氏度，`e_s` 单位近似为 hPa。它用于估算海面与空气中的水汽含量差异。

### 无线电折射率 N

代码注释采用 ITU-R P.453 常见形式：

```text
N = 77.6 / T * (P + 4810 e / T)
```

其中 `T` 为开尔文温度，`P` 为气压，`e` 为水汽压。`N` 是无线电折射率单位。

### 修正折射率 M

为了把地球曲率影响折算进折射率廓线，代码使用修正折射率：

```text
M(z) = N(z) + (z / R_e) * 10^6
```

`R_e` 是地球半径。蒸发波导判断主要看 `M(z)` 的垂直梯度。

### 波导陷获条件

代码采用：

```text
dM/dz < 0
```

当修正折射率随高度下降时，射线会向海面方向弯曲，可能被近海面薄层陷获，形成超视距传播。

### 波导高度与强度

波导高度 `δ` 由近似梯度零点得到：

```text
dM/dz = 0
```

并限制在 `0 <= δ <= 35 m`。波导强度近似定义为：

```text
ΔM = |M(0) - M(δ)|
```

`ΔM` 越大，代表波导层内修正折射率变化越强。

### 临界频率

代码使用经验近似：

```text
f_c = 100 / δ^(3/2)  GHz
f_c_MHz = (100 / δ^(3/2)) * 1000
```

这用于判断当前频率是否更容易被波导俘获。

## 2. 大尺度路径损耗模型

### 自由空间路径损耗

```text
PL_FSPL = 32.4 + 20 log10(f_MHz) + 20 log10(d_km)
```

`f_MHz` 是频率 MHz，`d_km` 是距离 km。

### 双线地面反射模型

```text
PL_2ray = 40 log10(d) - 20 log10(h_tx) - 20 log10(h_rx)
```

`d` 是收发距离，`h_tx` 和 `h_rx` 是发射与接收天线高度。该公式体现直达径和海面反射径组合后的远距离趋势。

### 波导增益修正

```text
PL_effective = PL_raw - G_duct
```

波导增益 `G_duct` 由波导强度、收发天线是否位于波导层内、频率相对临界频率的关系共同决定。代码中的增益是工程可视化近似，用于表达“有波导时远距离覆盖增强”。

## 3. 接收功率与蜂窝指标

### EIRP

```text
EIRP = P_tx + G_tx - L_tx_cable
```

### 接收功率

```text
P_rx = EIRP - PL_effective + G_rx - L_rx_cable + fading
```

`fading` 包括阴影衰落、小尺度海面多径衰落和波浪动态扰动。

### 热噪声功率

```text
N = -174 + 10 log10(B) + NF
```

`B` 是带宽 Hz，`NF` 是接收机噪声系数 dB。

### SINR

```text
SINR = P_rx - N - I
```

当前页面中干扰项主要是展示性处理，受扰基站报警表达的是“波导导致同频干扰风险”，不是完整邻区干扰矩阵求解。

### RSRQ / RSSI 近似

```text
N_RB = floor(B_MHz * 1000 / (12 * SCS_kHz))
RSSI ≈ P_rx + 10 log10(N_RB) + 3
RSRQ ≈ P_rx - RSSI - 10 log10(N_RB)
```

这是用于界面联动显示的简化蜂窝指标。

## 4. 小尺度衰落与海面多径

### 阴影衰落

```text
shadow_target += random(-0.4, 0.4) * Δt
shadow = shadow + (shadow_target - shadow) * speed * Δt
```

再乘以距离相关系数，形成随时间缓慢变化的大尺度遮挡/环境起伏。

### 双线相位差

```text
Δφ ≈ 2π * 2 h_tx h_rx / (λ d)
```

它来自双线模型的远场路径差近似。

### 海面多径衰落

```text
F_sea = 10 log10(2 + 2 cos(Δφ + small_wave_phase))
```

当直达径和反射径同相时增强，反相时衰落。

### 波浪动态衰落

```text
F_wave = 1.5 * sin(2.3 d + 0.003 t)
```

这是可视化中的动态扰动项，用于让链路指标随海况轻微变化。

## 5. PE 抛物方程传播模型

代码中 `PESolver` 使用 Split-Step Fourier 思路，计算二维距离-高度剖面上的场强。

### 自由空间传播算子

```text
H(p) = exp(-j π^2 p^2 Δx / k0)
```

`p` 是垂直空间频率，`Δx` 是距离步长，`k0 = 2π / λ`。

### 折射率相位屏

```text
φ = k0 * Δn * Δx
ψ_new = ψ_old * exp(j φ)
n(z) ≈ 1 + M(z) * 10^-6
```

页面中 PE 结果主要用于二维场强/路径损耗热力图和曲线展示。

## 6. 射线追踪 RT 近似

代码中的 `DuctRayTracer` 是可视化射线追踪，不是完整商业 RT 引擎。

### 初始方向

```text
dir = (cos(azimuth) cos(elevation), sin(elevation), sin(azimuth) cos(elevation))
```

### 波导弯曲

```text
dθ ≈ dM/dz * 10^-6 * STEP * VIZ_SCALE
```

`dM/dz < 0` 时射线向下弯曲，更容易被波导陷获；`dM/dz > 0` 时射线趋向逃逸。

### 陷获与逃逸判断

```text
trapped = hasDuct && ray_y <= near_sea_level
escaped = ray_y > ductHeight && dir_y > 0
```

这用于控制橙色陷获射线和绿色逃逸射线的显示。

## 7. 传播时延

### 直射时延

```text
τ_direct = d / c
```

### 反射路径时延

```text
τ_reflect = L_reflect / c
```

### 波导多跳时延

单跳距离近似：

```text
L_hop ≈ 2 sqrt(2 R_e δ)
```

再估计跳数和路径长度：

```text
N_hop = ceil(d / L_hop)
L_duct ≈ d + N_hop * δ * 0.3
τ_duct = L_duct / c
```

最终显示最大时延：

```text
τ_max = max(τ_direct, τ_reflect, τ_duct)
```

## 8. 主陷获链路图案可视化

当前页面中的干扰基站到船体、干扰基站到受扰基站两条主陷获链路，采用与浅橙色示范陷获射线一致的图案表达。它们不再用亮暗点表达电磁相位差，而是作为“示范陷获曲线的目标方向延伸”显示。

```text
y(t) = lerp(y_base(t), y_guided(t), 1 - exp(-7t))
```

其中示范波导振荡项为：

```text
y_guided(t) = z_duct_center(t) + sin(5.5πt) * A_duct
z_duct_center(t) = SEA_LEVEL + δ * [0.48 + 0.04 cos(2πt)]
A_duct = max(0.8, 0.32δ)
```

这里的 `t` 是沿链路从发射端到接收端的归一化参数，`δ` 是蒸发波导高度。这样处理的目的是让主通信/干扰链路看起来就是浅橙色示范陷获射线的连续延伸，而不是额外的一套相位编码。

## 9. 波导同频干扰警示

当前对岸受扰基站报警由 Python 返回结果优先驱动：

```text
alarm = interferenceAlarm_from_python
```

Python 端先根据环境参数估计波导：

```text
ductExists = isTrapping && ductHeight > 0.5 && ductProbability >= 0.25
```

再估计干扰站到受扰站的等效接收干扰功率：

```text
P_interfere = EIRP - (PL_victim - G_duct) + G_rx - L_rx_cable
margin = P_interfere - victimThreshold
alarm = ductExists && margin >= -6 dB
```

风险等级近似为：

```text
high risk: alarm 且 margin >= 8 dB 或 ΔM >= 9
medium risk: alarm 但未达到 high risk
low risk: 未报警
```

当 Python 后端离线时，Three.js 保留前端 fallback：`ductModel.isTrapping && ductHeight > 0.5` 时显示波导干扰风险。含义是：当蒸发波导存在且干扰链路越过门限时，干扰基站信号可能被波导带到更远海域或对岸基站方向，形成原本频率规划中未考虑到的同频干扰风险。

## 10. 海面和船体运动可视化公式

海面高度由多个正弦波叠加：

```text
h(x,z,t) = Σ A_i sin((x d_x + z d_z) f_i + v_i t)
              cos(z f_i 0.7 + 0.6 v_i t)
              sin(x f_i 0.5 + 0.8 v_i t)
```

船体高度采样海面波高：

```text
y_boat = 1.2 + h(x_boat, z_boat, t)
```

船体横摇/纵摇由左右、前后采样波高差估计：

```text
roll  ≈ atan((h_right - h_left) / 2ε)
pitch ≈ atan((h_front - h_back) / 2ε)
```

这些公式用于增强视觉真实感，不参与严格信道求解。
