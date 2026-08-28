# Confirmo 精灵图（Sprite Sheet）规范

本文件记录 confirmo.love 社区精灵图画廊 [sprites.confirmo.love](https://sprites.confirmo.love/) 的精灵图制作规范。
本插件（`dsh-plugin-confirmo`）的抠图流水线、7 状态播放引擎与 README 中的状态表均以此规范为准。

> 规范来源：sprites.confirmo.love 网站上传页（`/upload`）与网站内置 AI 生成提示词模板（前端 JS 内嵌，中英文各一份）。
> 官方没有独立的规范文档页面；上传页只显示简短摘要（格式、网格、推荐尺寸），完整要求内嵌于网站代码。

---

## 硬性要求

### 格式

- PNG 或 JPG 均可（推荐 PNG 以减少压缩噪点）

### 背景与抠图

- 背景色必须是且只能是**纯品红（magenta）`#ff00ff`**：不要渐变/阴影/纹理/噪点/压缩噪点；不要出现第二种背景色像素；应用会自动把背景抠成透明
- 角色不要自带任何"背景/场景/地面/墙面/光斑/烟雾"等元素；除角色本身外，所有区域必须是纯品红背景
- 请避免在角色/道具/阴影中使用背景色（`#ff00ff` 或非常接近的品红色），否则会被一起抠掉
- 角色表面不要出现品红色反光/品红色轮廓光/品红色光晕（避免被误抠）

### 网格与尺寸

- 分成 **8 列 × 7 行**的网格，每一格必须是**正方形帧**（每帧宽高相等！）
- 每一帧与相邻帧必须紧挨着：不要留白/间隔/内边距/外边距；不要画网格线或分隔线（不要有任何缝隙！）
- 整体长宽比约为 **8:7**（≈1.1429）
- 推荐输出 4K 级别高分辨率（如 **4096×3584，每帧 512×512**），程序会等比例缩放到最终尺寸 **1024×896（每帧 128×128）**

### 动画连贯性

- 同一行表示同一个动画；从左到右是连续帧，循环播放
- Idle（第1行）需要有呼吸和眨眼的动作，不要画成完全静止不动的帧
- Sleepy（第4行）只画闭眼呼吸的帧，不要画打哈欠的帧（循环播放时不停打哈欠会很突兀）
- 同一个动画（同一行）相邻两帧之间的变化必须非常连贯：不要跳帧、不要突然大幅位移/大幅姿态变化/大幅表情变化、不要突然变焦或改变视角
- 角色在每一帧中的位置尽量一致（建议以画布中心对齐），不要裁切到边缘

### 质量

- 图像质量高：角色细节清晰、边缘锐利、无模糊/锯齿/压缩伪影

---

## 行含义（从上到下，7 行）

| 行 | 状态 | 英文关键词 |
|---|---|---|
| 第1行 | 待机 Idle | `idle` |
| 第2行 | 开心 Happy / Love | `happy, love` |
| 第3行 | 兴奋 Excited / Celebrate | `excited, celebrate` |
| 第4行 | 睡觉 Sleepy / Snoring | `sleepy, snoring` |
| 第5行 | 工作 Working | `working` |
| 第6行 | 生气 Angry / Surprised / Shy | `angry, surprised, shy` |
| 第7行 | 拖拽 Dragging | `dragging` |

> 与本插件 README 状态表一致：Row1 idle、Row2 happy（单击）、Row3 excited（双击）、
> Row4 sleepy（5 分钟无操作）、Row5 working（agent 运行中）、Row6 angry（连点 5 次/出错）、Row7 dragging（拖拽）。

---

## 画廊配套实现

- **上传页摘要**：`PNG, JPG, JPEG supported (8x7 grid layout, 56 frames)`；
  `Recommended: 1024x896px or 4096x3584px (aspect ratio ~8:7)`
- **播放引擎**：8 列 × 7 行网格常量、`fps: 8`、`animationRow` 行选择
- **抠图流水线**：边缘采样判定背景色（magenta 模式）→ 泛洪填充 → 白蒙版膨胀 → 距离场羽化 → 溢色去除（spill removal）
- **API 字段**：`frameCount: 56`、`frameWidth`、`frameHeight`、`spriteUrl`、`thumbnailUrl`、`processedThumbnailUrl`、`zipUrl`、`animationUrl`
- **本插件移植**：`lib/client.src.js` 内嵌同款流水线（`floodSim=0.7`、`similarity=0.5`），对非标准品红背景（如 Doraemon 深紫 `#B818A0`）也鲁棒

---

## 相关地址

- 画廊：https://sprites.confirmo.love/ （上传页 `/upload`，图片 API `https://api.sprites.confirmo.love/sprites`）
- 素材服务器：https://pub-sprites.confirmo.love/
- 官网：https://confirmo.love/
