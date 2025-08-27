#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""红队自动化扫描工具 - 信息收集缝合版

功能说明：
- 集成 Masscan 端口扫描、Rad 爬虫、dddd-red 漏洞扫描
- 支持批量目标扫描和多线程并发
- 内置16000+指纹识别规则和丰富POC库
- 覆盖国内外主流应用和设备漏洞检测
- 提供详细的日志记录和进度显示
- 支持代理、超时等高级配置

使用示例：
    python script.py -t targets.txt -o results --threads 5 --timeout 30
    python script.py -t targets.txt --proxy http://127.0.0.1:8080 --verbose

依赖库：
    colorama>=0.4.4 (彩色输出支持)
"""

import subprocess
import threading
import os
import sys
import time
import json
import argparse
import logging
from queue import Queue
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import shutil

# 尝试导入colorama用于彩色输出
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  # 自动重置颜色
    COLORAMA_AVAILABLE = True
except ImportError:
    # 如果没有colorama，定义空的颜色常量
    class _DummyColor:
        def __getattr__(self, name):
            return ''
    
    Fore = Back = Style = _DummyColor()
    COLORAMA_AVAILABLE = False

# -------------------------------
# 彩色输出和格式化函数
# -------------------------------
class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    def format(self, record):
        if COLORAMA_AVAILABLE:
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def print_banner() -> None:
    """打印程序启动横幅"""
    banner = f"""
{Fore.CYAN}{'='*70}
{Fore.CYAN}██████╗ ███████╗██████╗     ████████╗███████╗ █████╗ ███╗   ███╗
{Fore.CYAN}██╔══██╗██╔════╝██╔══██╗    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
{Fore.CYAN}██████╔╝█████╗  ██║  ██║       ██║   █████╗  ███████║██╔████╔██║
{Fore.CYAN}██╔══██╗██╔══╝  ██║  ██║       ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║
{Fore.CYAN}██║  ██║███████╗██████╔╝       ██║   ███████╗██║  ██║██║ ╚═╝ ██║
{Fore.CYAN}╚═╝  ╚═╝╚══════╝╚═════╝        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
{Fore.YELLOW}              红队自动化扫描工具 v2.0 - 信息收集缝合版
{Fore.GREEN}        集成 Masscan + Rad + dddd-red + 16000+指纹库
{Fore.CYAN}{'='*70}{Style.RESET_ALL}
    """
    print(banner)


def print_colored(text: str, color: str = '', style: str = '', end: str = '\n') -> None:
    """打印彩色文本
    
    Args:
        text: 要打印的文本
        color: 颜色（如 Fore.RED）
        style: 样式（如 Style.BRIGHT）
        end: 结束符
    """
    if COLORAMA_AVAILABLE:
        print(f"{color}{style}{text}{Style.RESET_ALL}", end=end)
    else:
        print(text, end=end)


def print_status(message: str, status: str = 'info', icon: str = '') -> None:
    """打印状态信息
    
    Args:
        message: 状态消息
        status: 状态类型 (info, success, warning, error)
        icon: 图标
    """
    colors = {
        'info': Fore.CYAN,
        'success': Fore.GREEN,
        'warning': Fore.YELLOW,
        'error': Fore.RED
    }
    
    icons = {
        'info': '🔍',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    
    color = colors.get(status, Fore.WHITE)
    display_icon = icon or icons.get(status, '')
    
    print_colored(f"{display_icon} {message}", color)


def print_progress_bar(current: int, total: int, prefix: str = '', suffix: str = '', 
                      length: int = 50, fill: str = '█') -> None:
    """打印进度条
    
    Args:
        current: 当前进度
        total: 总数
        prefix: 前缀文本
        suffix: 后缀文本
        length: 进度条长度
        fill: 填充字符
    """
    if total == 0:
        percent = 0
    else:
        percent = current / total
    
    filled_length = int(length * percent)
    bar = fill * filled_length + '-' * (length - filled_length)
    
    # 根据进度选择颜色
    if percent < 0.3:
        color = Fore.RED
    elif percent < 0.7:
        color = Fore.YELLOW
    else:
        color = Fore.GREEN
    
    print_colored(f'\r{prefix} |{bar}| {current}/{total} ({percent:.1%}) {suffix}', color, end='')
    
    if current == total:
        print()  # 完成时换行


def print_summary_table(stats: Dict) -> None:
    """打印扫描结果汇总表
    
    Args:
        stats: 统计数据字典
    """
    print_colored("\n" + "="*60, Fore.CYAN)
    print_colored("📊 扫描结果汇总", Fore.CYAN, Style.BRIGHT)
    print_colored("="*60, Fore.CYAN)
    
    table_data = [
        ("总目标数", stats.get('total_targets', 0)),
        ("完成扫描", stats.get('completed_targets', 0)),
        ("失败目标", stats.get('failed_targets', 0)),
        ("发现端口", stats.get('total_ports', 0)),
        ("发现漏洞", stats.get('total_vulnerabilities', 0)),
        ("扫描耗时", f"{stats.get('elapsed_time', 0):.1f}秒")
    ]
    
    for label, value in table_data:
        print_colored(f"  {label:<12}: {value}", Fore.WHITE)
    
    print_colored("="*60, Fore.CYAN)


def get_terminal_width() -> int:
    """获取终端宽度
    
    Returns:
        终端宽度，默认80
    """
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80


# -------------------------------
# 配置管理类
# -------------------------------
class ScanConfig:
    """扫描配置管理类"""
    
    def __init__(self):
        self.masscan_path = "masscan.exe"
        self.rad_path = "rad.exe"
        self.dddd_path = "dddd-red_cracked.exe"
        self.default_ports = "80,443,22,3389,8080,8443,9090"
        self.default_rate = 5000
        self.default_threads = 3
        self.default_timeout = 30
        
    def validate_tools(self) -> List[str]:
        """验证工具文件是否存在
        
        Returns:
            缺失的工具文件列表
        """
        missing_tools = []
        tools = {
            'masscan.exe': self.masscan_path,
            'rad.exe': self.rad_path,
            'dddd-red_cracked.exe': self.dddd_path
        }
        
        for tool_name, tool_path in tools.items():
            if not os.path.exists(tool_path):
                missing_tools.append(tool_name)
                
        return missing_tools


# -------------------------------
# 日志配置
# -------------------------------
def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
    """设置日志配置
    
    Args:
        verbose: 是否启用详细日志
        log_file: 日志文件路径
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # 创建根日志记录器
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 控制台处理器（使用彩色格式）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    if COLORAMA_AVAILABLE:
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # 禁用一些第三方库的详细日志
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


# -------------------------------
# 统计信息类
# -------------------------------
class ScanStats:
    """扫描统计信息类"""
    
    def __init__(self):
        self.total_targets = 0
        self.completed_targets = 0
        self.failed_targets = 0
        self.total_ports = 0
        self.total_vulnerabilities = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
        
    def add_completed_target(self, ports_found: int = 0, vulns_found: int = 0) -> None:
        """添加完成的目标统计
        
        Args:
            ports_found: 发现的端口数
            vulns_found: 发现的漏洞数
        """
        with self.lock:
            self.completed_targets += 1
            self.total_ports += ports_found
            self.total_vulnerabilities += vulns_found
            
    def add_failed_target(self) -> None:
        """添加失败的目标统计"""
        with self.lock:
            self.failed_targets += 1
            
    def get_progress(self) -> float:
        """获取扫描进度
        
        Returns:
            进度百分比 (0-1)
        """
        with self.lock:
            if self.total_targets == 0:
                return 0.0
            return (self.completed_targets + self.failed_targets) / self.total_targets
            
    def get_elapsed_time(self) -> float:
        """获取已用时间
        
        Returns:
            已用时间（秒）
        """
        return time.time() - self.start_time
        
    def to_dict(self) -> Dict:
        """转换为字典格式
        
        Returns:
            统计信息字典
        """
        with self.lock:
            return {
                'total_targets': self.total_targets,
                'completed_targets': self.completed_targets,
                'failed_targets': self.failed_targets,
                'total_ports': self.total_ports,
                'total_vulnerabilities': self.total_vulnerabilities,
                'elapsed_time': self.get_elapsed_time()
            }


# -------------------------------
# 核心扫描函数
# -------------------------------
def run_command_with_timeout(cmd: List[str], timeout: int = 30, cwd: str = None) -> tuple:
    """执行命令并设置超时
    
    Args:
        cmd: 命令列表
        timeout: 超时时间（秒）
        cwd: 工作目录
        
    Returns:
        (返回码, 标准输出, 标准错误)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            encoding='utf-8',
            errors='ignore'
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"命令执行超时 ({timeout}秒)"
    except Exception as e:
        return -1, "", f"命令执行失败: {str(e)}"


def parse_masscan_output(output: str) -> List[Dict]:
    """解析Masscan输出结果
    
    Args:
        output: Masscan输出文本
        
    Returns:
        端口信息列表
    """
    ports = []
    for line in output.strip().split('\n'):
        if line.strip() and 'open' in line:
            try:
                # 解析格式: Discovered open port 80/tcp on 192.168.1.1
                parts = line.split()
                if len(parts) >= 6:
                    port_info = parts[3]  # 80/tcp
                    ip = parts[5]  # 192.168.1.1
                    port, protocol = port_info.split('/')
                    ports.append({
                        'ip': ip,
                        'port': int(port),
                        'protocol': protocol,
                        'status': 'open'
                    })
            except (ValueError, IndexError):
                continue
    return ports


def scan_target(target: str, config: ScanConfig, stats: ScanStats, 
               output_dir: str, ports: str, rate: int, timeout: int, 
               proxy: Optional[str] = None) -> Dict:
    """扫描单个目标
    
    Args:
        target: 目标地址
        config: 扫描配置
        stats: 统计信息
        output_dir: 输出目录
        ports: 端口列表
        rate: 扫描速率
        timeout: 超时时间
        proxy: 代理设置
        
    Returns:
        扫描结果字典
    """
    result = {
        'target': target,
        'timestamp': datetime.now().isoformat(),
        'status': 'failed',
        'masscan': {'status': 'not_run', 'ports': []},
        'rad': {'status': 'not_run', 'urls': []},
        'dddd': {'status': 'not_run', 'vulnerabilities': []},
        'errors': []
    }
    
    try:
        # 创建目标专用目录
        target_dir = os.path.join(output_dir, target.replace('/', '_').replace(':', '_'))
        os.makedirs(target_dir, exist_ok=True)
        
        # 阶段1: Masscan端口扫描
        print_status(f"[{target}] 开始Masscan端口扫描", 'info', '🔍')
        masscan_cmd = [
            config.masscan_path,
            target,
            '-p', ports,
            '--rate', str(rate),
            '--wait', '3'
        ]
        
        returncode, stdout, stderr = run_command_with_timeout(masscan_cmd, timeout)
        
        if returncode == 0:
            print_status(f"[{target}] Masscan扫描完成", 'success', '✅')
            result['masscan']['status'] = 'completed'
            
            # 保存Masscan结果
            masscan_file = os.path.join(target_dir, 'masscan_result.txt')
            with open(masscan_file, 'w', encoding='utf-8') as f:
                f.write(stdout)
            
            # 解析端口信息
            ports_found = parse_masscan_output(stdout)
            result['masscan']['ports'] = ports_found
            
            if ports_found:
                print_status(f"[{target}] 发现 {len(ports_found)} 个开放端口", 'success', '🎯')
                
                # 生成dddd-red目标文件
                dddd_targets_file = os.path.join(target_dir, 'dddd_targets.txt')
                with open(dddd_targets_file, 'w', encoding='utf-8') as f:
                    for port_info in ports_found:
                        f.write(f"http://{port_info['ip']}:{port_info['port']}\n")
                        if port_info['port'] in [443, 8443]:  # HTTPS端口
                            f.write(f"https://{port_info['ip']}:{port_info['port']}\n")
                
                # 阶段2: Rad爬虫扫描
                print_status(f"[{target}] 开始Rad爬虫扫描", 'info', '🕷️')
                rad_cmd = [
                    config.rad_path,
                    '--target-file', dddd_targets_file,
                    '--text-output', os.path.join(target_dir, 'rad_result.txt')
                ]
                
                if proxy:
                    rad_cmd.extend(['--proxy', proxy])
                
                returncode, stdout, stderr = run_command_with_timeout(rad_cmd, timeout)
                
                if returncode == 0:
                    print_status(f"[{target}] Rad爬虫扫描完成", 'success', '✅')
                    result['rad']['status'] = 'completed'
                    
                    # 读取Rad结果
                    rad_result_file = os.path.join(target_dir, 'rad_result.txt')
                    if os.path.exists(rad_result_file):
                        with open(rad_result_file, 'r', encoding='utf-8') as f:
                            urls = [line.strip() for line in f if line.strip()]
                            result['rad']['urls'] = urls
                            print_status(f"[{target}] 发现 {len(urls)} 个URL", 'success', '🔗')
                else:
                    print_status(f"[{target}] Rad扫描失败: {stderr}", 'warning', '⚠️')
                    result['rad']['status'] = 'failed'
                    result['errors'].append(f"Rad扫描失败: {stderr}")
                
                # 阶段3: dddd-red漏洞扫描
                print_status(f"[{target}] 开始dddd-red漏洞扫描", 'info', '🛡️')
                dddd_cmd = [
                    config.dddd_path,
                    '-t', dddd_targets_file,
                    '-o', os.path.join(target_dir, 'dddd_result.txt')
                ]
                
                if proxy:
                    dddd_cmd.extend(['--proxy', proxy])
                
                returncode, stdout, stderr = run_command_with_timeout(dddd_cmd, timeout * 2)  # dddd-red需要更长时间
                
                if returncode == 0:
                    print_status(f"[{target}] dddd-red扫描完成", 'success', '✅')
                    result['dddd']['status'] = 'completed'
                    
                    # 读取dddd-red结果
                    dddd_result_file = os.path.join(target_dir, 'dddd_result.txt')
                    if os.path.exists(dddd_result_file):
                        with open(dddd_result_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # 简单解析漏洞信息（根据实际输出格式调整）
                            vulns = []
                            for line in content.split('\n'):
                                if 'vulnerability' in line.lower() or 'vuln' in line.lower():
                                    vulns.append(line.strip())
                            result['dddd']['vulnerabilities'] = vulns
                            
                            if vulns:
                                print_status(f"[{target}] 发现 {len(vulns)} 个潜在漏洞", 'warning', '🚨')
                            else:
                                print_status(f"[{target}] 未发现明显漏洞", 'info', '🛡️')
                else:
                    print_status(f"[{target}] dddd-red扫描失败: {stderr}", 'warning', '⚠️')
                    result['dddd']['status'] = 'failed'
                    result['errors'].append(f"dddd-red扫描失败: {stderr}")
            else:
                print_status(f"[{target}] 未发现开放端口，跳过后续扫描", 'info', '🔒')
        else:
            print_status(f"[{target}] Masscan扫描失败: {stderr}", 'error', '❌')
            result['masscan']['status'] = 'failed'
            result['errors'].append(f"Masscan扫描失败: {stderr}")
            stats.add_failed_target()
            return result
        
        # 保存单个目标的结果
        result_file = os.path.join(output_dir, f"{target.replace('/', '_').replace(':', '_')}_result.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        result['status'] = 'completed'
        
        # 更新统计信息
        ports_count = len(result['masscan']['ports'])
        vulns_count = len(result['dddd']['vulnerabilities'])
        stats.add_completed_target(ports_count, vulns_count)
        
        print_status(f"[{target}] 扫描完成", 'success', '🎉')
        
    except Exception as e:
        error_msg = f"扫描目标 {target} 时发生错误: {str(e)}"
        print_status(error_msg, 'error', '❌')
        result['errors'].append(error_msg)
        stats.add_failed_target()
    
    return result


# -------------------------------
# 工作线程和进度监控
# -------------------------------
def worker(task_queue: Queue, results: List, config: ScanConfig, stats: ScanStats,
          output_dir: str, ports: str, rate: int, timeout: int, proxy: Optional[str]) -> None:
    """工作线程函数
    
    Args:
        task_queue: 任务队列
        results: 结果列表
        config: 扫描配置
        stats: 统计信息
        output_dir: 输出目录
        ports: 端口列表
        rate: 扫描速率
        timeout: 超时时间
        proxy: 代理设置
    """
    while True:
        try:
            target = task_queue.get(timeout=1)
            if target is None:
                break
                
            result = scan_target(target, config, stats, output_dir, ports, rate, timeout, proxy)
            results.append(result)
            
            task_queue.task_done()
        except:
            break


def progress_monitor(stats: ScanStats, stop_event: threading.Event) -> None:
    """进度监控线程
    
    Args:
        stats: 统计信息
        stop_event: 停止事件
    """
    last_progress = -1
    
    while not stop_event.is_set():
        current_progress = stats.get_progress()
        
        # 只在进度变化时更新显示
        if abs(current_progress - last_progress) > 0.01:  # 1%的变化
            with stats.lock:
                completed = stats.completed_targets
                total = stats.total_targets
                ports = stats.total_ports
                vulns = stats.total_vulnerabilities
                elapsed = stats.get_elapsed_time()
            
            print_progress_bar(
                completed, total,
                prefix='扫描进度',
                suffix=f'已完成: {completed}/{total} | 端口: {ports} | 漏洞: {vulns} | 耗时: {elapsed:.1f}s'
            )
            last_progress = current_progress
        
        time.sleep(0.5)


# -------------------------------
# 辅助函数
# -------------------------------
def load_targets(target_file: str) -> List[str]:
    """加载目标列表
    
    Args:
        target_file: 目标文件路径
        
    Returns:
        目标列表
    """
    targets = []
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            for line in f:
                target = line.strip()
                if target and not target.startswith('#'):
                    targets.append(target)
    except Exception as e:
        print_status(f"读取目标文件失败: {str(e)}", 'error')
        return []
    
    return targets


def save_final_report(results: List[Dict], output_dir: str, stats: ScanStats) -> None:
    """保存最终扫描报告
    
    Args:
        results: 扫描结果列表
        output_dir: 输出目录
        stats: 统计信息
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(output_dir, f'scan_report_{timestamp}.json')
    
    report = {
        'scan_info': {
            'timestamp': datetime.now().isoformat(),
            'total_targets': len(results),
            'statistics': stats.to_dict()
        },
        'results': results
    }
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print_status(f"扫描报告已保存: {report_file}", 'success')
    except Exception as e:
        print_status(f"保存扫描报告失败: {str(e)}", 'error')


# -------------------------------
# 主函数
# -------------------------------
def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(
        description='红队自动化扫描工具 - 信息收集缝合版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python script.py -t targets.txt
  python script.py -t targets.txt -o my_results --threads 5
  python script.py -t targets.txt --proxy http://127.0.0.1:8080 --verbose
        """
    )
    
    parser.add_argument('-t', '--targets', required=True,
                       help='目标文件路径')
    parser.add_argument('-o', '--output', default='scan_results',
                       help='输出目录 (默认: scan_results)')
    parser.add_argument('-p', '--ports', default='80,443,22,3389,8080,8443,9090',
                       help='扫描端口列表 (默认: 80,443,22,3389,8080,8443,9090)')
    parser.add_argument('-r', '--rate', type=int, default=5000,
                       help='Masscan扫描速率 (默认: 5000)')
    parser.add_argument('--threads', type=int, default=3,
                       help='并发线程数 (默认: 3)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='单个工具超时时间/秒 (默认: 30)')
    parser.add_argument('--proxy',
                       help='代理设置 (例: http://127.0.0.1:8080)')
    parser.add_argument('--verbose', action='store_true',
                       help='启用详细日志输出')
    parser.add_argument('--log-file',
                       help='日志文件路径')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose, args.log_file)
    
    # 打印启动横幅
    print_banner()
    
    # 初始化配置
    config = ScanConfig()
    
    # 验证工具文件
    print_status("检查工具文件...", 'info')
    missing_tools = config.validate_tools()
    if missing_tools:
        print_status(f"缺少工具文件: {missing_tools}", 'error')
        print_status("请确保以下文件存在于当前目录:", 'info')
        for tool in missing_tools:
            print_status(f"  - {tool}", 'info')
        sys.exit(1)
    print_status("工具文件检查完成", 'success')
    
    # 创建输出目录
    print_status(f"创建输出目录: {args.output}", 'info')
    os.makedirs(args.output, exist_ok=True)
    
    # 加载目标
    print_status(f"加载目标文件: {args.targets}", 'info')
    targets = load_targets(args.targets)
    if not targets:
        print_status("未找到有效目标", 'error')
        sys.exit(1)
    print_status(f"加载了 {len(targets)} 个目标", 'success')
    
    # 显示扫描配置
    print_colored("\n📋 扫描配置:", Fore.CYAN, Style.BRIGHT)
    config_info = [
        f"  目标数量: {len(targets)}",
        f"  扫描端口: {args.ports}",
        f"  扫描速率: {args.rate}",
        f"  并发线程: {args.threads}",
        f"  超时时间: {args.timeout}秒",
        f"  输出目录: {args.output}"
    ]
    if args.proxy:
        config_info.append(f"  代理设置: {args.proxy}")
    
    for info in config_info:
        print_colored(info, Fore.WHITE)
    
    # 初始化统计信息
    stats = ScanStats()
    stats.total_targets = len(targets)
    
    # 创建任务队列和结果列表
    task_queue = Queue()
    results = []
    
    # 添加任务到队列
    for target in targets:
        task_queue.put(target)
    
    # 启动进度监控
    stop_event = threading.Event()
    progress_thread = threading.Thread(
        target=progress_monitor,
        args=(stats, stop_event)
    )
    progress_thread.daemon = True
    progress_thread.start()
    
    print_status("\n开始扫描...", 'info', '🚀')
    
    try:
        # 启动工作线程
        threads = []
        for i in range(args.threads):
            t = threading.Thread(
                target=worker,
                args=(task_queue, results, config, stats, args.output, 
                     args.ports, args.rate, args.timeout, args.proxy)
            )
            t.daemon = True
            t.start()
            threads.append(t)
        
        # 等待所有任务完成
        task_queue.join()
        
        # 停止进度监控
        stop_event.set()
        progress_thread.join(timeout=1)
        
        # 等待所有线程结束
        for t in threads:
            t.join(timeout=1)
        
        print_colored("\n🎉 扫描完成!", Fore.GREEN, Style.BRIGHT)
        
        # 显示结果汇总
        print_summary_table(stats.to_dict())
        
        # 保存最终报告
        save_final_report(results, args.output, stats)
        
        print_status(f"\n📁 结果保存在: {os.path.abspath(args.output)}", 'success')
        
        # 检查是否发现漏洞
        total_vulns = stats.total_vulnerabilities
        if total_vulns > 0:
            print_status(f"🚨 发现 {total_vulns} 个潜在漏洞，请及时处理!", 'warning')
        
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  用户中断扫描", Fore.YELLOW, Style.BRIGHT)
        stop_event.set()
    except Exception as e:
        print_status(f"扫描过程中发生错误: {str(e)}", 'error')
        stop_event.set()
    finally:
        # 确保进度监控线程停止
        stop_event.set()


if __name__ == "__main__":
    main()