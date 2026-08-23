# Sprite 素材目录

本目录存放精灵图资源。

## 结构

```
docs/sprites/<sprite-id>/
├── sprite.png|jpg      # 8列×7行=56帧精灵图（原始素材）
├── thumbnail.png|jpg   # 画廊缩略图
└── processed.png       # 处理后的单角色透明图（仅部分 sprite 有）
```

## 来源

- 清单：`dsh-plugin-confirmo/sprite_list.json`（60 个热门 sprite 的 URL）
- 服务器：`pub-sprites.confirmo.love`（素材版权归各上传作者所有，仅作本地归档）
- 下载时间：2026-08

## 重新下载

运行本目录下的下载脚本：

```bash
node docs/sprites/download-sprites.mjs
```

脚本会读取 `dsh-plugin-confirmo/sprite_list.json`，按每个 sprite 的
`spriteUrl` / `thumbnailUrl` / `processedThumbnailUrl` 字段下载到对应 `<sprite-id>/` 文件夹。
已存在且大小相同的文件会跳过（断点续传），可随时重复运行。
