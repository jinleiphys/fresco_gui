# FRESCO Studio

FRESCO 耦合道计算的现代图形用户界面

**直接核反应的耦合道计算**

---

## 功能特点

### 双输入模式
- **交互式向导**: 所有反应类型的逐步引导输入
  - 弹性散射
  - 非弹性散射
  - 转移反应
- **文本编辑器**: 直接编辑 FRESCO 输入文件

### 支持的反应类型
- **弹性散射**: 带光学势的简单弹靶反应
- **非弹性散射**: 带耦合定义的激发态
- **转移反应**: 完整支持包括：
  - 自动查找结合能（氘核、氚核、3He、α粒子）
  - 壳模型量子数（p壳、sd壳）
  - 从核数据库获取正确的宇称赋值
  - 5套势能（入射、出射、弹核束缚、剩余核束缚、remnant）
  - 重叠函数和耦合配置

### 可视化与输出
- **实时绘图**: 截面和角分布可视化
- **输出日志**: 带颜色编码的实时 FRESCO 输出监控
- **现代设计**: 支持浅色和深色主题的简洁界面

### 核数据库
- 基于 AME2020 原子质量评估的自动质量查询
- 常见核素的基态自旋和宇称
- 转移反应的分离能

---

## 安装指南

### 第0步：安装前提条件

安装 FRESCO Studio 之前，您需要：

1. **运行 macOS 或 Linux 的电脑**（Windows 用户可使用 WSL）
2. **Anaconda 或 Miniconda** - 用于 Python 环境管理
3. **Fortran 编译器** - 用于编译 FRESCO

#### 安装 Anaconda/Miniconda（如果没有的话）

**macOS:**
```bash
# 下载并安装 Miniconda（轻量版）
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh
# 按提示操作，在初始化 conda 时选择"yes"
# 然后重启终端
```

**Linux:**
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
# 按提示操作，在初始化 conda 时选择"yes"
# 然后重启终端
```

#### 安装 Fortran 编译器

**macOS:**
```bash
# 如果没有 Homebrew，先安装它
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 gfortran
brew install gcc
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install gfortran
```

---

### 第1步：下载代码

#### 方法A：下载 ZIP 压缩包（最简单 - 无需 Git）

1. 访问: https://github.com/jinleiphys/fresco_gui
2. 点击绿色的 **"Code"** 按钮
3. 点击 **"Download ZIP"**
4. 将 ZIP 文件解压到一个文件夹（如桌面或文档）
5. 打开终端，进入该文件夹：
   ```bash
   cd ~/Desktop/fresco_gui-main
   # 或者您解压的位置
   ```

#### 方法B：使用 Git（推荐）

如果您已安装 Git：
```bash
cd ~  # 进入主目录
git clone https://github.com/jinleiphys/fresco_gui.git
cd fresco_gui
```

---

### 第2步：运行安装脚本（推荐）

进入 fresco_gui 文件夹后，运行：

```bash
chmod +x setup_gui.sh
./setup_gui.sh
```

此脚本将自动：
1. 创建名为 `fresco_gui` 的 conda 环境
2. 安装所有 Python 依赖
3. 编译 FRESCO Fortran 代码
4. 完成所有设置，可立即使用

**等待脚本完成**（可能需要几分钟）。

---

### 第3步：运行 FRESCO Studio

安装完成后：

```bash
./run_fresco_gui.sh
```

图形界面应该会打开！

---

### 手动安装（备选方案）

如果自动安装不成功，可以手动安装：

**1. 创建并激活 conda 环境：**
```bash
conda create -n fresco_gui python=3.10
conda activate fresco_gui
```

**2. 安装 Python 依赖：**
```bash
cd fresco_gui
pip install -r requirements.txt
```

**3. 编译 FRESCO：**
```bash
cd ../fresco_code/source
make
```

**4. 运行图形界面：**
```bash
cd ../../fresco_gui
python main.py
```

---

### 更新 FRESCO Studio

获取最新版本：

**如果使用 Git：**
```bash
cd fresco_gui
git pull
```

**如果下载的 ZIP：**
下载新的 ZIP 并替换旧文件夹。

---

## 使用方法

### 运行图形界面

```bash
# 使用启动脚本（推荐）
./run_fresco_gui.sh

# 或手动运行
conda activate fresco_gui
cd fresco_gui
python main.py
```

### 使用向导

1. **反应设置**:
   - 输入反应方程式（如转移反应 `c12(d,p)c13`，弹性散射 `p+ni58`）
   - 设置束流能量
   - 向导自动检测反应类型

2. **粒子配置**:
   - 查看/修改粒子属性（质量、自旋、宇称）
   - 数值从核数据库预填充

3. **势能**（弹性/非弹性散射）:
   - 配置光学势
   - 添加多个势分量（库仑势、体积势、表面势、自旋轨道势）

4. **转移反应特定步骤**:
   - **出射道**: 配置出射粒子和剩余核
   - **重叠函数**: 设置结合能和谱因子
   - 量子数从壳模型自动计算

5. **生成与运行**:
   - 检查生成的输入
   - 运行 FRESCO 计算
   - 在绘图面板查看结果

### 使用文本编辑器

1. **输入参数**:
   - 创建新输入文件或打开现有文件（文件 → 打开）
   - 直接编辑 FRESCO 输入
   - 使用"显示示例"按钮查看样本输入

2. **运行计算**:
   - 保存输入文件（文件 → 保存）
   - 点击"运行"或按 Ctrl+R
   - 在输出日志标签页监控进度

3. **查看结果**:
   - 切换到绘图标签页
   - 从下拉菜单选择绘图类型
   - 使用 matplotlib 工具栏进行缩放/平移/保存

### 键盘快捷键

- `Ctrl+N`: 新建文件
- `Ctrl+O`: 打开文件
- `Ctrl+S`: 保存文件
- `Ctrl+R`: 运行 FRESCO
- `Ctrl+.`: 停止计算
- `Ctrl+Q`: 退出程序

---

## 主题

图形界面支持浅色和深色主题：
- 通过"视图 → 主题"菜单切换主题
- 浅色主题：清晰明亮的界面（默认）
- 深色主题：长时间使用更护眼

---

## 系统要求

- Python 3.8 或更高版本
- PySide6 (Qt for Python)
- matplotlib
- numpy
- scipy（可选）
- 已编译的 FRESCO 可执行文件

---

## 常见问题

### 找不到 FRESCO 可执行文件

如果出现关于 FRESCO 可执行文件的错误：
1. 确保 FRESCO 已编译：`cd fresco_code/source && make`
2. 检查错误信息中的可执行文件路径
3. 可以设置 FRESCO_EXE 环境变量指向您的可执行文件

### 导入错误

如果遇到导入错误：
```bash
conda activate fresco_gui
pip install --upgrade -r requirements.txt
```

### 图形界面无法启动

在 macOS 上，可能需要安装系统依赖：
```bash
brew install qt6
```

---

## 技术支持

如有问题或疑问：
- 联系邮箱: jinl@tongji.edu.cn
- 查看 fresco_code/man 目录中的 FRESCO 文档

---

## 致谢

使用以下技术构建：
- PySide6 (Qt for Python)
- matplotlib 科学绑图
- AME2020 原子质量评估数据
