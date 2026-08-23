# Sprite 素材目录（不入库）

本目录存放从 `sprites.confirmo.love` 下载的精灵图资源，**已被 .gitignore 排除**，不会提交到仓库。
如需要可随时重新下载。

## 结构

```
docs/assets/<sprite-id>/
├── sprite.png|jpg      # 8列×7行=56帧精灵图（原始素材）
├── thumbnail.png|jpg   # 画廊缩略图
└── processed.png       # 处理后的单角色透明图（仅部分 sprite 有）
```

## 来源

- 清单：`dsh-plugin-confirmo/sprite_list.json`（60 个热门 sprite 的 URL）
- 服务器：`pub-sprites.confirmo.love`（素材版权归各上传作者所有，仅作本地归档）
- 下载时间：2026-08

## 重新下载

按 `sprite_list.json` 中每个 sprite 的 `spriteUrl` / `thumbnailUrl` / `processedThumbnailUrl`
字段下载到对应 `<sprite-id>/` 文件夹即可（脚本见仓库 issue 或自行编写）。
