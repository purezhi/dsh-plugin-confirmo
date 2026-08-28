# Confirmo 精灵图 AI 生成提示词

本文提供可直接投喂给 AI 图像生成器（DALL·E 3 / Midjourney / Stable Diffusion / 即梦 / 文心一格 等）的提示词，
目标：生成**严格符合 sprites.confirmo.love 规范**的 8×7 精灵图（Sprite Sheet）。

> 规范细节见 [`docs/sprite-spec.md`](sprite-spec.md)。
> 提示词分三个版本：**完整版**（效果最好）、**精简版**（token 有限时）、**负面提示词**（生成器不支持正向描述时使用）。
> 每个版本都分中英文。

---

## ⚠️ 生成器通病与应对

AI 生成器对"精确网格"普遍不敏感，常见失败：

| 失败现象 | 应对 |
|---|---|
| 帧数不对（7×6、9×8、少帧） | 反复强调 **exactly 8 columns × 7 rows = 56 square frames** |
| 帧之间有白线/网格线/留白 | 强调 **frames must be flush, touching, no gaps, no grid lines** |
| 帧不是正方形（被拉伸） | 强调 **each frame must be a perfect square** |
| 背景不是纯品红 | 强调 **background is flat solid magenta #FF00FF only** |
| 一行内动作不连贯 | 强调 **each row is one animation, frames L→R continuous** |
| 角色位置漂移 | 强调 **character centered and consistent in every frame** |
| 行顺序错乱 | 在提示词里**逐行列出**（从顶部 Idle 到底部 Dragging） |

---

## 1️⃣ 完整版（推荐）

### 中文版

```
请生成一张精灵图（sprite sheet），用于桌面宠物动画。画面只有一张图，整图比例为 8:7（宽:高）。

【网格硬性要求】
- 图片必须分成 8 列 × 7 行 = 56 个完全相等的正方形格子（帧）
- 每一格必须是正方形（宽 = 高）；整图推荐 4096×3584，每帧 512×512
- 所有帧必须紧贴排列：帧与帧之间绝对不要留白、不要间隙、不要网格线、不要边框、不要分割线
- 同一行的 8 帧是同一个动画的连续帧，从左到右播放，可无缝循环

【背景硬性要求】
- 除角色本身外，整张图的背景必须是纯品红（magenta）纯色，颜色值 #FF00FF
- 背景必须完全平整：无渐变、无阴影、无纹理、无噪点、无光斑、无文字
- 角色身上/道具/阴影中绝对不能出现品红色或接近品红的颜色（否则会被抠掉）
- 角色不要有背景、场景、地面、墙面、烟雾、光斑等任何环境元素

【角色要求】
- 角色：使用上传图片，要高度还原
- 风格：3D 卡通渲染，干净、可爱、统一光照与配色
- 每个角色在帧中居中、位置一致、不要裁切到边缘；单帧内角色占帧面积约 60-80%
- 相邻两帧之间的动作变化必须平滑连贯：无跳帧、无突然位移、无突然变脸
- 所有角色保持同一尺寸、同一画风、同一朝向

【7 行动画（从上到下）】
第1行 Idle 待机：角色轻微呼吸起伏 + 眨眼，动作最安静
第2行 Happy 开心：微笑、挥手或比心等开心小动作
第3行 Excited 兴奋：跳跃、欢呼、双手举起等庆祝动作，幅度比第2行大
第4行 Sleepy 睡觉：闭眼、身体放松、轻微呼吸起伏（不要打哈欠、不要 Zzz 文字）
第5行 Working 工作：对着电脑/键盘打字，或拿着工具专注工作的动作
第6行 Angry 生气：皱眉、跺脚、双手叉腰或鼓腮等生气动作
第7行 Dragging 拖拽：身体被向上提起、双脚悬空挣扎，或拖着重物的动作

只输出这一张精灵图（PNG），不要输出任何其他内容、文字或说明。
```

### 英文版

```
Generate a single sprite sheet image for a desktop pet animation. The image is the ONLY output, aspect ratio 8:7 (width : height).

[GRID - STRICT]
- The image must be divided into EXACTLY 8 columns × 7 rows = 56 equal square cells (frames)
- Every cell must be a PERFECT SQUARE (width == height); recommended 4096×3584 px, 512×512 per frame
- All frames must be FLUSH and TOUCHING: absolutely NO gaps, NO whitespace, NO grid lines, NO borders, NO separators between frames
- The 8 frames in each row form ONE continuous animation, played left to right, seamlessly loopable

[BACKGROUND - STRICT]
- The background must be FLAT SOLID MAGENTA #FF00FF everywhere except the character itself
- Background must be completely flat: NO gradients, shadows, textures, noise, light spots, or text
- The character, props, and shadows must NEVER contain magenta or near-magenta colors (they would be keyed out)
- NO environment elements: no background scenes, ground, walls, smoke, or light halos

[CHARACTER]
- Character: <character name/description>, e.g., a cute yellow cat
- Style: clean 3D cartoon render, cute, unified lighting and colors
- Character centered and position-consistent in every frame; do not crop to frame edges; character occupies roughly 60-80% of each frame
- Adjacent frames must transition smoothly: NO frame skipping, NO sudden position jumps, NO sudden expression changes
- Keep the same size, art style, and facing direction across all frames

[7 ROWS, TOP TO BOTTOM]
Row 1 - Idle: gentle breathing + blinking, the calmest motion
Row 2 - Happy: smiling, waving, or a heart gesture
Row 3 - Excited: jumping, cheering, arms raised — bigger motion than Row 2
Row 4 - Sleepy: eyes closed, relaxed body, gentle breathing (NO yawning, NO "Zzz" text)
Row 5 - Working: typing at a computer/keyboard, or focused work with a tool
Row 6 - Angry: frowning, stamping foot, hands on hips, or puffed cheeks
Row 7 - Dragging: body lifted upward, feet dangling, or pulling a heavy object

Output ONLY this one sprite sheet image (PNG). No text, no captions, no extra content.
```

---

## 2️⃣ 精简版（token 有限 / 短提示词接口）

### 中文版

```
一张精灵图 sprite sheet：8列×7行=56个正方形帧，帧与帧紧贴无间隙无网格线；
纯品红#FF00FF纯色背景，无渐变无文字；3D卡通可爱角色，居中、动作连贯；
从上到下7行依次为：待机(呼吸眨眼)/开心/兴奋/睡觉(闭眼)/工作/生气/拖拽；
整图8:7比例，高分辨率。角色：<角色描述>。只输出这张图。
```

### 英文版

```
A sprite sheet: exactly 8 columns × 7 rows = 56 square frames, frames flush with NO gaps or grid lines;
flat solid magenta #FF00FF background, no gradients or text; clean 3D cute character, centered, smooth motion;
7 rows top-to-bottom: idle (breathing/blinking) / happy / excited / sleepy (eyes closed) / working / angry / dragging;
8:7 aspect ratio, high resolution. Character: <description>. Output ONLY the sprite sheet image.
```

---

## 3️⃣ 负面提示词（用于支持 negative prompt 的生成器）

### 中文版

```
不要网格线、不要分割线、不要边框、不要留白间隙、不要帧错位、不要非正方形帧、
不要透明背景、不要黑色/白色/其他颜色背景、不要渐变背景、不要阴影背景、不要场景、
不要地面、不要墙面、不要文字、不要水印、不要角色叠加、不要重复角色、不要模糊、
不要锯齿、不要拉伸变形、不要品红出现在角色身上、不要角色被裁切、不要多余装饰
```

### 英文版

```
grid lines, separators, borders, gaps between frames, misaligned frames, non-square frames,
transparent background, black or white background, gradient background, shadowed background,
scene, ground, wall, text, watermark, overlapping characters, duplicated characters, blur,
aliasing, distortion, magenta on character, cropped character, extra decorations
```

---

## 4️⃣ 生成后自检清单

生成后先做快速检查（可肉眼或让插件加载验证）：

- [ ] 尺寸比例 ≈ 8:7（如 4096×3584 / 2048×1792 / 1024×896）
- [ ] 四角与边缘是纯品红 `#FF00FF`
- [ ] 数帧：每行恰好 8 帧、共 7 行（56 帧）
- [ ] 每帧是正方形（无拉伸）
- [ ] 帧间无白线/网格线
- [ ] 角色身上无品红色块（会被抠掉）
- [ ] 每行动作与要求一致、帧间连贯
- [ ] 可直接用 `docs/sprites/download-sprites.mjs` 的抠图逻辑验证（或放入插件测试）

> 若生成器反复失败，可尝试：先生成"单行 8 帧"的横幅再拼接，或用 ControlNet/Sketch 固定网格后生成。

---

## 5️⃣ 官方原版提示词（sprites.confirmo.love 内置，供对照）

> 画廊网站上传页"AI 生成"功能内置的提示词原文（从网站前端 JS 提取），也是本仓库提示词的规范依据。

**中文原文（节选）**：

```
请生成一张精灵图（sprite sheet）

硬性要求：
- PNG 或 JPG 均可（推荐 PNG 以减少压缩噪点）
- 背景色必须是且只能是纯品红（magenta）#ff00ff：不要渐变/阴影/纹理/噪点/压缩噪点；
  不要出现第二种背景色像素；应用会自动把背景抠成透明
- 角色不要自带任何"背景/场景/地面/墙面/光斑/烟雾"等元素
- 请避免在角色/道具/阴影中使用背景色（#ff00ff 或非常接近的品红色），否则会被一起抠掉
- 分成 8 列 × 7 行的网格，每一格必须是正方形帧（每帧宽高相等！）
- 每一帧与相邻帧必须紧挨着：不要留白/间隔/内边距/外边距；不要画网格线或分隔线
- 整体长宽比约为 8:7（≈1.1429）
- 推荐输出 4K 级别高分辨率（如 4096×3584，每帧 512×512）
- 同一行表示同一个动画；从左到右是连续帧，循环播放
- Idle（第1行）需要有呼吸和眨眼的动作
- Sleepy（第4行）只画闭眼呼吸的帧，不要画打哈欠的帧
- 相邻两帧之间的变化必须非常连贯：不要跳帧、不要突然大幅位移/姿态/表情变化
- 角色在每一帧中的位置尽量一致（建议以画布中心对齐），不要裁切到边缘

行含义（从上到下）：
- 第1行：Idle（idle）
- 第2行：Happy / Love（happy, love）
- 第3行：Excited / Celebrate（excited, celebrate）
- 第4行：Sleepy / Snoring（sleepy, snoring）
- 第5行：Working（working）
- 第6行：Angry / Surprised / Shy（angry, surprised, shy）
- 第7行：Dragging（dragging）
```

**英文原文（节选）**：结构与中文版一致（`Generate a sprite sheet image. Strict Requirements: ... Row 1: Idle ... Row 7: Dragging`）。
