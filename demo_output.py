#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红队扫描工具输出效果演示

本脚本用于演示优化后的彩色输出效果，无需实际扫描即可查看界面效果。

使用方法:
    python demo_output.py
"""

import time
import sys
from pathlib import Path

# 添加当前目录到路径，以便导入script.py中的函数
sys.path.insert(0, str(Path(__file__).parent))

try:
    from script import (
        print_banner, print_status, print_colored, print_progress_bar, 
        print_summary_table, Fore, Style, COLORAMA_AVAILABLE
    )
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保script.py文件存在且可导入")
    sys.exit(1)


def demo_banner():
    """演示横幅显示"""
    print_banner()
    time.sleep(1)


def demo_status_messages():
    """演示状态消息"""
    print_colored("\n🎭 状态消息演示:", Fore.CYAN + Style.BRIGHT)
    print_colored("="*50, Fore.CYAN)
    
    status_demos = [
        ('info', '系统初始化完成'),
        ('success', '工具验证通过'),
        ('info', '开始扫描目标: 192.168.1.100'),
        ('warning', '发现潜在风险'),
        ('error', '连接超时'),
        ('success', '扫描任务完成: example.com')
    ]
    
    for status, message in status_demos:
        print_status(message, status)
        time.sleep(0.5)


def demo_progress_bar():
    """演示进度条"""
    print_colored("\n📊 进度条演示:", Fore.CYAN + Style.BRIGHT)
    print_colored("="*50, Fore.CYAN)
    
    total = 20
    for i in range(total + 1):
        print_progress_bar(
            i, total,
            prefix='扫描进度',
            suffix=f'已完成: {i}/{total} | 端口: {i*3} | 漏洞: {i//5}'
        )
        time.sleep(0.1)
    
    print()  # 换行


def demo_configuration_display():
    """演示配置信息显示"""
    print_colored("\n📋 配置信息演示:", Fore.CYAN + Style.BRIGHT)
    print_colored("="*50, Fore.CYAN)
    
    config_info = [
        "  目标数量: 15",
        "  扫描端口: 80,443,22,3389,8080,8443,9090",
        "  扫描速率: 5000",
        "  并发线程: 3",
        "  超时时间: 30秒",
        "  输出目录: scan_results",
        "  代理设置: http://127.0.0.1:8080"
    ]
    
    for info in config_info:
        print_colored(info, Fore.WHITE)
        time.sleep(0.3)


def demo_summary_table():
    """演示汇总表格"""
    print_colored("\n📈 结果汇总演示:", Fore.CYAN + Style.BRIGHT)
    
    demo_stats = {
        'total_targets': 15,
        'completed_targets': 12,
        'failed_targets': 3,
        'total_ports': 45,
        'total_vulnerabilities': 8,
        'elapsed_time': 127.5
    }
    
    print_summary_table(demo_stats)


def demo_scan_simulation():
    """演示扫描过程模拟"""
    print_colored("\n🔍 扫描过程模拟:", Fore.CYAN + Style.BRIGHT)
    print_colored("="*50, Fore.CYAN)
    
    targets = [
        "192.168.1.100",
        "example.com",
        "test.local",
        "10.0.0.50"
    ]
    
    for i, target in enumerate(targets):
        print_status(f"[{target}] 开始Masscan端口扫描", 'info', '🔍')
        time.sleep(0.5)
        
        if i % 3 == 0:  # 模拟发现端口
            print_status(f"[{target}] 发现 3 个开放端口", 'success', '🎯')
            time.sleep(0.3)
            print_status(f"[{target}] 开始Rad爬虫扫描", 'info', '🕷️')
            time.sleep(0.5)
            print_status(f"[{target}] 发现 12 个URL", 'success', '🔗')
            time.sleep(0.3)
            print_status(f"[{target}] 开始dddd-red漏洞扫描", 'info', '🛡️')
            time.sleep(0.5)
            
            if i == 0:  # 第一个目标发现漏洞
                print_status(f"[{target}] 发现 2 个潜在漏洞", 'warning', '🚨')
            else:
                print_status(f"[{target}] 未发现明显漏洞", 'info', '🛡️')
            
            print_status(f"[{target}] 扫描完成", 'success', '🎉')
        else:  # 模拟无端口或失败
            if i % 2 == 1:
                print_status(f"[{target}] 未发现开放端口，跳过后续扫描", 'info', '🔒')
            else:
                print_status(f"[{target}] 连接超时", 'error', '❌')
        
        time.sleep(0.5)
        print()  # 空行分隔


def demo_completion():
    """演示完成信息"""
    print_colored("\n🎉 扫描完成!", Fore.GREEN + Style.BRIGHT)
    print_status("📁 结果保存在: /path/to/scan_results", 'success')
    print_status("🚨 发现 2 个潜在漏洞，请及时处理!", 'warning')


def main():
    """主演示函数"""
    print_colored("🎨 DDDD-RED 彩色输出效果演示", Fore.MAGENTA + Style.BRIGHT)
    print_colored("="*60, Fore.MAGENTA)
    
    if not COLORAMA_AVAILABLE:
        print("⚠️  警告: 未安装colorama库，将显示无彩色版本")
        print("建议运行: pip install colorama")
        print()
    
    try:
        # 1. 横幅演示
        demo_banner()
        
        # 2. 状态消息演示
        demo_status_messages()
        
        # 3. 进度条演示
        demo_progress_bar()
        
        # 4. 配置信息演示
        demo_configuration_display()
        
        # 5. 扫描过程演示
        demo_scan_simulation()
        
        # 6. 结果汇总演示
        demo_summary_table()
        
        # 7. 完成信息演示
        demo_completion()
        
        print_colored("\n✨ 演示完成! 这就是优化后的扫描工具界面效果。", Fore.CYAN + Style.BRIGHT)
        
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  演示被用户中断", Fore.YELLOW + Style.BRIGHT)
    except Exception as e:
        print_colored(f"\n❌ 演示过程中发生错误: {str(e)}", Fore.RED + Style.BRIGHT)


if __name__ == "__main__":
    main()