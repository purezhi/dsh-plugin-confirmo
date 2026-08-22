#!/usr/bin/env bash
# ============================================================================
# DSH Confirmo Plugin - 一键安装脚本
# 在 DeepSeek Harness (DSH) 的 Web UI 里放一只 Confirmo 桌宠(复刻 confirmo.love):
#   - 默认形象:confirmo.love 的同款黄猫(浮动/眨眼/耳动/胡须/尾巴动画)
#   - 支持社区 sprite:sprites.confirmo.love 的 8x7 精灵图(纯品红 #ff00ff
#     背景自动抠除,8fps 播放;单击播 Excited、拖拽播 Dragging 行)
#   - 右键打开菜单:切换热门 sprite / 回到默认猫 / 调整大小(96/128/160)
#   - 位置、所选 sprite、大小持久化(localStorage),应用升级后依然存在
#   - 注册在 ~/.dsh(用户配置),不碰应用安装目录
# ============================================================================
set -euo pipefail

# --- 1. 定位本脚本所在目录(插件包根) --------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="$SCRIPT_DIR/dsh-plugin-confirmo"
DSH_HOME="${DSH_HOME:-$HOME/.dsh}"

echo "=============================================="
echo " DSH Confirmo Plugin 安装"
echo "=============================================="

# --- 2. 检查插件包是否完整 ------------------------------------------------
if [ ! -f "$PKG_DIR/package.json" ] || [ ! -f "$PKG_DIR/lib/client.js" ]; then
  echo "✗ 错误: 找不到插件包文件, 请确认本脚本与 dsh-plugin-confirmo/ 在同一目录"
  echo "  (若缺少 lib/client.js, 先运行: node dsh-plugin-confirmo/build.js)"
  exit 1
fi

# --- 3. 检查 DSH 主目录 ----------------------------------------------------
if [ ! -d "$DSH_HOME" ]; then
  echo "✗ 错误: 未找到 DSH 主目录 ($DSH_HOME)。请先安装/运行一次 DSH。"
  exit 1
fi
echo "✓ DSH 主目录: $DSH_HOME"

# --- 4. 拷贝插件到 profiles 共享 node_modules ------------------------------
SHARED_NM="$DSH_HOME/profiles/node_modules"
TARGET="$SHARED_NM/dsh-plugin-confirmo"
mkdir -p "$SHARED_NM"
rm -rf "$TARGET"
cp -R "$PKG_DIR" "$TARGET"
echo "✓ 插件包已安装: $TARGET"

# --- 5. 注册到 desktop / web profile ---------------------------------------
patch_file() {
  local profile="$1"
  local patch="$DSH_HOME/profiles/$profile/cordis.patch.yml"
  if [ ! -f "$patch" ]; then
    echo "  (跳过 $profile: 无 cordis.patch.yml)"
    return
  fi
  if grep -q "dsh-plugin-confirmo" "$patch" 2>/dev/null; then
    echo "  ($profile 已注册, 跳过)"
    return
  fi
  cat >> "$patch" <<EOF

# Confirmo companion plugin: a client-only UI plugin (empty node apply) whose
# browser half is discovered via the package.json dshClient declaration.
- insert:
    - id: confirmo
      name: dsh-plugin-confirmo
EOF
  echo "  ✓ 已注册到 $profile"
}

# web profile 需要插件链接(desktop 走共享目录即可)
link_web() {
  local web_nm="$DSH_HOME/profiles/web/node_modules"
  if [ -d "$DSH_HOME/profiles/web" ] && [ ! -e "$web_nm/dsh-plugin-confirmo" ]; then
    mkdir -p "$web_nm"
    ln -sfn "$TARGET" "$web_nm/dsh-plugin-confirmo"
    echo "  ✓ 已链接到 web profile"
  fi
}

echo "注册插件..."
patch_file "desktop"
patch_file "web"
link_web

# --- 6. 完成 ---------------------------------------------------------------
echo ""
echo "=============================================="
echo " ✓ 安装完成!"
echo ""
echo " 使用方法:"
echo "   1. 重启 DSH Desktop(或重新运行 dsh web)"
echo "   2. 界面左下角(或上次记住的位置)出现 Confirmo 桌宠"
echo "   3. 按住拖拽移动; 单击播放反应动画"
echo "   4. 右键打开菜单: 切换热门 sprite / 默认猫 / 大小"
echo ""
echo " 卸载: 运行 uninstall.sh 或手动删除:"
echo "   rm -rf $TARGET"
echo "   并移除 cordis.patch.yml 里的 confirmo 注册段"
echo "=============================================="
