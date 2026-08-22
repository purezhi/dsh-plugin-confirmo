#!/usr/bin/env bash
# ============================================================================
# DSH Confirmo Plugin - 卸载脚本
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DSH_HOME="${DSH_HOME:-$HOME/.dsh}"
TARGET="$DSH_HOME/profiles/node_modules/dsh-plugin-confirmo"

echo "卸载 DSH Confirmo Plugin..."

# 1. 删除插件包
if [ -d "$TARGET" ]; then
  rm -rf "$TARGET"
  echo "✓ 已删除: $TARGET"
else
  echo "(未找到插件包, 跳过)"
fi

# 2. 删除 web profile 链接
WEB_LINK="$DSH_HOME/profiles/web/node_modules/dsh-plugin-confirmo"
if [ -L "$WEB_LINK" ] || [ -e "$WEB_LINK" ]; then
  rm -rf "$WEB_LINK"
  echo "✓ 已删除 web 链接: $WEB_LINK"
fi

# 3. 从 cordis.patch.yml 移除注册段
for profile in desktop web; do
  patch="$DSH_HOME/profiles/$profile/cordis.patch.yml"
  [ -f "$patch" ] || continue
  if grep -q "dsh-plugin-confirmo" "$patch" 2>/dev/null; then
    # 移除从 "Confirmo companion plugin" 注释到包含 dsh-plugin-confirmo 的 insert 行
    perl -0pi -e 's/\n*# Confirmo companion plugin:.*?- insert:\n    - id: confirmo\n      name: dsh-plugin-confirmo\n*//s' "$patch"
    echo "✓ 已从 $profile 的 cordis.patch.yml 移除注册"
  else
    echo "(跳过 $profile: 未注册)"
  fi
done

echo ""
echo "完成。请重启 DSH Desktop 生效。"
