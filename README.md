# DDDD-RED v2.0 - 红队自动化扫描工具 (信息收集缝合版)

## 📋 项目简介

本项目是一个集成化的红队渗透测试工具套件，专注于信息收集和漏洞发现的缝合版本。整合了多个开源安全工具和丰富的POC库，实现自动化的三阶段扫描流程：

1. **端口扫描** - 使用 Masscan 进行快速端口发现
2. **Web爬虫** - 使用 Rad 进行网站爬取和URL收集  
3. **漏洞扫描** - 使用 dddd-red 进行深度漏洞检测

## 🚀 主要特性

### 🎯 核心能力
- ✅ **三阶段扫描** - Masscan端口发现 → Rad爬虫分析 → dddd-red漏洞检测
- ✅ **丰富POC库** - 500+ 漏洞检测规则，覆盖主流应用和设备
- ✅ **指纹识别** - 16,000+ 指纹规则，精准识别目标服务
- ✅ **国产化适配** - 专门针对国内OA、ERP、网络设备优化

### 🛠️ 技术特性
- ✅ **模块化设计** - 清晰的代码结构，易于维护和扩展
- ✅ **命令行参数** - 支持丰富的配置选项，无需修改代码
- ✅ **多线程并发** - 支持批量目标扫描，提高效率
- ✅ **错误处理** - 完善的异常处理和超时控制
- ✅ **进度监控** - 实时显示扫描进度和统计信息
- ✅ **彩色输出** - 美观的彩色终端界面，状态一目了然
- ✅ **进度条显示** - 动态进度条，实时展示扫描状态
- ✅ **日志记录** - 详细的日志输出，支持文件保存
- ✅ **结果保存** - JSON格式的结构化结果输出
- ✅ **代理支持** - 支持HTTP代理配置
- ✅ **跨平台兼容** - 兼容Windows和Linux系统

### 📊 POC覆盖范围
- 🏢 **OA办公系统**: 泛微、致远、用友、金和、蓝凌等
- 💼 **ERP管理系统**: 用友、金蝶、明源云、智联云采等
- 🌐 **Web框架**: Apache、Nginx、Tomcat、Spring、ThinkPHP等
- 🔧 **网络设备**: 华为、锐捷、H3C、深信服等
- 📱 **物联网设备**: 海康威视、大华、宇视等
- 🗄️ **数据库中间件**: MySQL、Redis、MongoDB、Elasticsearch等

## 📦 环境要求

- Python 3.8+
- Windows/Linux 操作系统
- 工具文件：`masscan.exe`、`rad.exe`、`dddd-red_cracked.exe`
- 推荐安装：`colorama` 库（用于彩色输出）

## 🛠️ 安装配置

### 1. 克隆项目
```bash
git clone https://github.com/3072638260/dddd-reds-v2.git
cd dddd-reds-v2
```

### 2. 安装依赖
```bash
# 安装彩色输出支持（推荐）
pip install colorama

# 或安装所有依赖
pip install -r requirements.txt
```

### 3. 准备工具文件
确保以下工具文件存在于项目目录：
- `masscan.exe` - 端口扫描工具
- `rad.exe` - Web爬虫工具
- `dddd-red_cracked.exe` - 漏洞扫描工具

### 4. 准备目标文件
创建目标文件（如 `targets.txt`），每行一个目标：
```
192.168.1.1
example.com
10.0.0.0/24
```

### 5. 测试安装
```bash
# 查看帮助信息
python script.py --help

# 运行演示脚本查看彩色输出效果
python demo_output.py
```

## 📖 使用方法

### 基本用法

```bash
# 基础扫描
python script.py -t targets.txt

# 指定输出目录
python script.py -t targets.txt -o my_results

# 自定义端口和线程数
python script.py -t targets.txt --ports "80,443,8080" --threads 5
```

### 高级用法

```bash
# 使用代理扫描
python script.py -t targets.txt --proxy http://127.0.0.1:8080

# 启用详细日志
python script.py -t targets.txt --verbose --log-file scan.log

# 自定义超时和扫描速率
python script.py -t targets.txt --timeout 60 --rate 10000

# 完整配置示例
python script.py -t targets.txt -o results \\
  --ports "80,443,22,3389,8080,8443,9090" \\
  --threads 8 --timeout 45 --rate 8000 \\
  --proxy http://127.0.0.1:8080 \\
  --verbose --log-file detailed.log
```

## ⚙️ 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-t, --targets` | 必需 | - | 目标文件路径 |
| `-o, --output` | 可选 | scan_results | 输出目录 |
| `-p, --ports` | 可选 | 80,443,22,3389,8080,8443,9090 | 扫描端口列表 |
| `-r, --rate` | 可选 | 5000 | Masscan扫描速率 |
| `--threads` | 可选 | 3 | 并发线程数 |
| `--timeout` | 可选 | 30 | 单个工具超时时间(秒) |
| `--proxy` | 可选 | - | 代理设置 |
| `--verbose` | 可选 | False | 启用详细日志 |
| `--log-file` | 可选 | - | 日志文件路径 |

## 📁 项目结构

```
dddd-reds-v2/
├── script.py                    # 主扫描脚本
├── demo_output.py               # 输出效果演示
├── requirements.txt             # 依赖库列表
├── targets_example.txt          # 示例目标文件
├── config/                      # 配置文件目录
│   ├── allpoc/                 # POC漏洞库
│   ├── dict/                   # 字典文件
│   ├── finger.yaml             # 指纹识别规则
│   ├── dir.yaml                # 目录扫描配置
│   └── api-config.yaml         # API配置文件
├── common/                      # 公共组件
│   └── webserver/              # Web服务器组件
└── README.md                    # 项目说明文档
```

## 📊 输出结果

扫描完成后，会在输出目录生成以下文件：

```
scan_results/
├── target1_result.json          # 单个目标的详细结果
├── target2_result.json
├── scan_report_timestamp.json   # 总体扫描报告
└── target1/                     # 目标详细数据
    ├── masscan_result.txt
    ├── dddd_targets.txt
    ├── rad_result.txt
    └── dddd_result.txt
```

## 🔧 配置优化

### 性能调优

1. **线程数配置**
   - CPU密集型：线程数 = CPU核心数
   - 网络密集型：线程数 = CPU核心数 × 2-4
   - 建议范围：3-10个线程

2. **扫描速率**
   - 内网扫描：10000-50000
   - 外网扫描：1000-5000
   - 谨慎环境：500-1000

3. **超时设置**
   - 快速扫描：15-30秒
   - 标准扫描：30-60秒
   - 深度扫描：60-120秒

## 🛡️ 安全建议

1. **授权确认**
   - 确保所有目标都在授权范围内
   - 避免扫描生产环境和敏感系统

2. **代理使用**
   - 在敏感环境中使用代理隐藏源IP
   - 配置合适的代理链路

3. **日志管理**
   - 启用详细日志记录操作过程
   - 定期清理和归档日志文件

## 🐛 故障排除

### 常见问题

1. **工具文件不存在**
   ```
   错误：缺少工具文件: ['masscan.exe']
   解决：确保工具文件在项目目录中
   ```

2. **目标文件格式错误**
   ```
   错误：未找到有效目标
   解决：检查目标文件格式，确保每行一个有效目标
   ```

3. **权限不足**
   ```
   错误：Masscan执行失败
   解决：以管理员权限运行，或检查工具权限
   ```

## 🔮 优化空间与发展规划

### 🚀 高优先级优化项
1. **信息收集能力增强**
   - 集成网络空间搜索引擎 (FOFA、Hunter、Shodan)
   - 添加子域名收集功能 (subfinder、amass)
   - 增强端口服务识别 (nmap service detection)
   - 目录爆破集成 (dirsearch、gobuster)

2. **扫描流程优化**
   - 实现管道式扫描架构
   - 资产统一管理和去重
   - 漏洞关联分析和风险评估
   - 攻击面自动化分析

3. **结果聚合增强**
   - HTML可视化报告生成
   - Excel数据分析报告
   - 漏洞去重和分级管理
   - 历史扫描数据对比

### 🔧 中优先级优化项
1. **性能优化**
   - 智能线程池管理
   - 内存优化和流式处理
   - 扫描结果缓存机制
   - 断点续传功能

2. **配置管理**
   - 分层配置文件结构
   - 热更新配置支持
   - 扫描模板和预设
   - 自定义规则导入

### 📊 低优先级优化项
1. **Web管理界面**
   - 基于Flask的Web控制台
   - 任务管理和调度
   - 实时监控面板
   - 多用户权限管理

2. **分布式扫描**
   - 多节点协同扫描
   - 任务分发和负载均衡
   - 结果汇总和同步

> 📋 详细优化分析请参考: [OPTIMIZATION_ANALYSIS.md](OPTIMIZATION_ANALYSIS.md)

## 📝 更新日志

### v2.0 - 信息收集缝合版
- 重构代码架构，提高可维护性
- 添加命令行参数支持
- 增强错误处理和日志记录
- 实现进度监控和统计功能
- 支持代理和超时配置
- 优化结果输出格式
- 添加彩色终端界面
- 集成16,000+指纹识别规则
- 内置500+漏洞检测POC
- 专门优化国产化应用检测

## ⚠️ 免责声明

本工具仅用于授权的安全测试和教育目的。使用者需要：

1. 确保拥有目标系统的合法授权
2. 遵守当地法律法规和道德规范
3. 不得用于非法攻击或恶意活动
4. 对使用本工具造成的任何后果承担责任

## 📞 技术支持

如有问题或建议，请通过以下方式联系：

- 提交 Issue：[GitHub Issues](https://github.com/3072638260/dddd-reds-v2/issues)
- 查看文档：项目 Wiki 页面
- 社区讨论：[Discussions](https://github.com/3072638260/dddd-reds-v2/discussions)

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**注意：请在合法授权的环境中使用本工具，并遵守相关法律法规。**