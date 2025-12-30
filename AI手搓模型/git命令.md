# 开始
# 1. 删除本地 .git 目录（彻底移除本地 Git 历史）
rm -rf .git  # Windows 用：rmdir /s /q .git

# 2. 重新初始化 Git 仓库
git init

# 3. 关联远程仓库（替换为你的远程仓库地址）
git remote add origin https://github.com/xprocessing/neocz2025.git

# 4. 拉取远程主分支（允许合并无关历史，因重新初始化后历史为空）
git pull origin main --allow-unrelated-histories

# 5. （若有本地修改）提交并推送
git add .
git commit -m "初始化仓库并同步远程"
git push origin main