#!/usr/bin/env python3
"""
IPTV源收集器 - 从多个公开源收集国内电视频道
"""
import json
import os
import re
import sys
import time
import socket
import struct
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.error import URLError
from datetime import datetime

# ============================================
# 频道映射 - 标准化频道名称
# ============================================
CHANNEL_MAP = {
    # 央视
    "CCTV1": ["CCTV1", "CCTV-1", "央视综合", "中央一套", "CCTV1综合", "cctv1hd"],
    "CCTV2": ["CCTV2", "CCTV-2", "央视财经", "中央二套", "CCTV2财经"],
    "CCTV3": ["CCTV3", "CCTV-3", "央视综艺", "中央三套", "CCTV3综艺"],
    "CCTV4": ["CCTV4", "CCTV-4", "央视中文国际", "中央四套", "CCTV4中文国际"],
    "CCTV5": ["CCTV5", "CCTV-5", "央视体育", "中央五套", "CCTV5体育"],
    "CCTV5+": ["CCTV5+", "CCTV-5+", "央视体育赛事", "CCTV5+体育赛事"],
    "CCTV6": ["CCTV6", "CCTV-6", "央视电影", "中央六套", "CCTV6电影"],
    "CCTV7": ["CCTV7", "CCTV-7", "央视国防军事", "中央七套", "CCTV7国防军事"],
    "CCTV8": ["CCTV8", "CCTV-8", "央视电视剧", "中央八套", "CCTV8电视剧"],
    "CCTV9": ["CCTV9", "CCTV-9", "央视纪录", "中央九套", "CCTV9纪录"],
    "CCTV10": ["CCTV10", "CCTV-10", "央视科教", "中央十套", "CCTV10科教"],
    "CCTV11": ["CCTV11", "CCTV-11", "央视戏曲", "中央十一套", "CCTV11戏曲"],
    "CCTV12": ["CCTV12", "CCTV-12", "央视社会与法", "中央十二套", "CCTV12社会与法"],
    "CCTV13": ["CCTV13", "CCTV-13", "央视新闻", "中央十三套", "CCTV13新闻"],
    "CCTV14": ["CCTV14", "CCTV-14", "央视少儿", "中央十四套", "CCTV14少儿"],
    "CCTV15": ["CCTV15", "CCTV-15", "央视音乐", "中央十五套", "CCTV15音乐"],
    "CCTV16": ["CCTV16", "CCTV-16", "央视奥林匹克", "CCTV16奥林匹克"],
    "CCTV17": ["CCTV17", "CCTV-17", "央视农业农村", "CCTV17农业农村"],
    # 卫视
    "湖南卫视": ["湖南卫视", "湖南台", "湖南HD", "HNTV"],
    "浙江卫视": ["浙江卫视", "浙江台", "浙江HD", "ZJTV"],
    "东方卫视": ["东方卫视", "上海卫视", "上海台", "上海HD", "DFTV"],
    "江苏卫视": ["江苏卫视", "江苏台", "江苏HD", "JSTV"],
    "北京卫视": ["北京卫视", "北京台", "北京HD", "BJTV"],
    "广东卫视": ["广东卫视", "广东台", "广东HD", "GDTV"],
    "深圳卫视": ["深圳卫视", "深圳台", "深圳HD", "SZTV"],
    "天津卫视": ["天津卫视", "天津台", "天津HD", "TJTV"],
    "山东卫视": ["山东卫视", "山东台", "山东HD", "SDTV"],
    "安徽卫视": ["安徽卫视", "安徽台", "安徽HD", "AHTV"],
    "江西卫视": ["江西卫视", "江西台", "江西HD", "JXTV"],
    "湖北卫视": ["湖北卫视", "湖北台", "湖北HBTV", "HBTV"],
    "四川卫视": ["四川卫视", "四川台", "四川HD", "SCTV"],
    "重庆卫视": ["重庆卫视", "重庆台", "重庆HD", "CQTV"],
    "河南卫视": ["河南卫视", "河南台", "河南HD", "HNTV2"],
    "河北卫视": ["河北卫视", "河北台", "河北HD", "HEBTV"],
    "辽宁卫视": ["辽宁卫视", "辽宁台", "辽宁HD", "LNTV"],
    "吉林卫视": ["吉林卫视", "吉林台", "吉林HD", "JLTV"],
    "黑龙江卫视": ["黑龙江卫视", "黑龙江台", "黑龙江HD", "HLJTV"],
    "福建卫视": ["福建卫视", "东南卫视", "福建台", "福建HD", "FJTV"],
    "广西卫视": ["广西卫视", "广西台", "广西HD", "GXTV"],
    "云南卫视": ["云南卫视", "云南台", "云南HD", "YNTV"],
    "贵州卫视": ["贵州卫视", "贵州台", "贵州HD", "GZTV"],
    "山西卫视": ["山西卫视", "山西台", "山西HD", "SXTV"],
    "陕西卫视": ["陕西卫视", "陕西台", "陕西HD", "SXTV2"],
    "甘肃卫视": ["甘肃卫视", "甘肃台", "甘肃HD", "GSTV"],
    "海南卫视": ["海南卫视", "海南台", "海南HD", "HAINANTV"],
    "新疆卫视": ["新疆卫视", "新疆台", "新疆HD", "XJTV"],
    "西藏卫视": ["西藏卫视", "西藏台", "西藏HD", "XZTV"],
    "内蒙古卫视": ["内蒙古卫视", "内蒙古台", "内蒙古HD", "NMGT"],
    "宁夏卫视": ["宁夏卫视", "宁夏台", "宁夏HD", "NXTV"],
    "青海卫视": ["青海卫视", "青海台", "青海HD", "QHTV"],
    "三沙卫视": ["三沙卫视", "三沙台", "SSTV"],
    "厦门卫视": ["厦门卫视", "厦门台", "XMTV"],
    "金鹰卡通": ["金鹰卡通", "金鹰卡通卫视"],
    "卡酷少儿": ["卡酷少儿", "卡酷动画"],
    "炫动卡通": ["炫动卡通"],
    "优漫卡通": ["优漫卡通"],
}

# 需要收集的频道名称列表
TARGET_CHANNELS = list(CHANNEL_MAP.keys())


def fetch_url(url, timeout=10, headers=None):
    """安全获取URL内容"""
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    if headers:
        default_headers.update(headers)
    req = Request(url, headers=default_headers)
    try:
        resp = urlopen(req, timeout=timeout)
        return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  [WARN] 获取失败 {url}: {e}")
        return None


def normalize_channel_name(name):
    """标准化频道名称"""
    name = name.strip().replace(" ", "")
    for standard_name, aliases in CHANNEL_MAP.items():
        for alias in aliases:
            if alias.lower() in name.lower() or name.lower() in alias.lower():
                return standard_name
    return name


def parse_m3u(content):
    """解析M3U内容，返回 [(频道名, url, tvg_id, logo), ...]"""
    entries = []
    if not content:
        return entries
    lines = content.strip().split("\n")
    current_name = None
    current_tvg = ""
    current_logo = ""
    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF:"):
            # 提取频道名
            match = re.search(r',(.+)$', line)
            if match:
                current_name = match.group(1).strip()
            # 提取 tvg-id
            tvg_match = re.search(r'tvg-id="([^"]*)"', line)
            if tvg_match:
                current_tvg = tvg_match.group(1)
            # 提取 logo
            logo_match = re.search(r'tvg-logo="([^"]*)"', line)
            if logo_match:
                current_logo = logo_match.group(1)
        elif line and not line.startswith("#") and current_name:
            entries.append((current_name, line.strip(), current_tvg, current_logo))
            current_name = None
            current_tvg = ""
            current_logo = ""
    return entries


def parse_txt(content):
    """解析TXT格式 (频道名,url)"""
    entries = []
    if not content:
        return entries
    for line in content.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "," in line:
            parts = line.split(",", 1)
            if len(parts) == 2:
                name, url = parts[0].strip(), parts[1].strip()
                if url.startswith("http"):
                    entries.append((name, url, "", ""))
        elif "://" in line:
            entries.append((line, line.strip(), "", ""))
    return entries


# ============================================
# 公开源列表
# ============================================
SOURCES = [
    # M3U 格式源
    {"name": "YueChan", "type": "m3u", "url": "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u"},
    {"name": "YanG", "type": "m3u", "url": "https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u"},
    {"name": "fanmingming", "type": "m3u", "url": "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u"},
    {"name": "wcb1978", "type": "m3u", "url": "https://raw.githubusercontent.com/wcb19780807/20231115/main/tvlive.m3u"},
    {"name": "Kimentan", "type": "m3u", "url": "https://raw.githubusercontent.com/Kimentanm/aptv/main/iptv/m3u/hn.m3u"},
    {"name": "ssili126", "type": "m3u", "url": "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u"},
    {"name": "Meroser", "type": "m3u", "url": "https://raw.githubusercontent.com/Meroser/IPTV/main/tvlive.m3u"},
    {"name": "zzz", "type": "m3u", "url": "https://raw.githubusercontent.com/zmofei/zmofei.github.io/main/docs/live/tv.m3u"},
    {"name": "iptv-org-cn", "type": "m3u", "url": "https://raw.githubusercontent.com/iptv-org/iptv/master/countries/cn.m3u"},
    # TXT 格式源
    {"name": "live-txt", "type": "txt", "url": "https://raw.githubusercontent.com/xiaoxiaoyang/livetv/main/live.txt"},
    {"name": "Huan", "type": "m3u", "url": "https://raw.githubusercontent.com/huan/iptv-live/main/iptv.m3u"},
    {"name": "muziling", "type": "txt", "url": "https://raw.githubusercontent.com/muziling/iptv/main/tv.txt"},
]


def collect_all_sources():
    """收集所有源"""
    all_entries = []
    print("开始收集 IPTV 源...")
    for src in SOURCES:
        print(f"  收集: {src['name']} ({src['type']})...")
        content = fetch_url(src["url"], timeout=15)
        if content:
            if src["type"] == "m3u":
                entries = parse_m3u(content)
            else:
                entries = parse_txt(content)
            print(f"    → 获取 {len(entries)} 个频道")
            all_entries.extend(entries)
        else:
            print(f"    → 获取失败")
    print(f"\n总共收集到 {len(all_entries)} 个条目")
    return all_entries


def match_target_channels(entries):
    """匹配目标频道，去重"""
    matched = {}  # {channel_name: [(url, source, latency), ...]}
    unmatched = []
    for name, url, tvg_id, logo in entries:
        standard_name = normalize_channel_name(name)
        if standard_name in TARGET_CHANNELS:
            if standard_name not in matched:
                matched[standard_name] = []
            matched[standard_name].append((url, name, tvg_id, logo))
        else:
            # 尝试模糊匹配
            found = False
            for target in TARGET_CHANNELS:
                if target in name or name in target:
                    if target not in matched:
                        matched[target] = []
                    matched[target].append((url, name, tvg_id, logo))
                    found = True
                    break
            if not found:
                unmatched.append((name, url))
    print(f"匹配到 {len(matched)} 个目标频道，共 {sum(len(v) for v in matched.values())} 个源")
    return matched


def check_stream(url, timeout=8):
    """检查单个流是否可用，返回延迟(ms)"""
    try:
        if url.startswith("http"):
            start = time.time()
            req = Request(url, headers={"User-Agent": "VLC/3.0.0"})
            req.method = "HEAD"
            try:
                resp = urlopen(req, timeout=timeout)
                latency = int((time.time() - start) * 1000)
                return True, latency
            except:
                # HEAD失败，尝试GET读取少量数据
                start = time.time()
                req = Request(url, headers={
                    "User-Agent": "VLC/3.0.0",
                    "Range": "bytes=0-1024"
                })
                resp = urlopen(req, timeout=timeout)
                _ = resp.read(1024)
                latency = int((time.time() - start) * 1000)
                return True, latency
        else:
            return False, 99999
    except Exception:
        return False, 99999


def verify_sources_parallel(matched, max_workers=30, max_per_channel=3):
    """并行验证源，返回每个频道最优的N个源"""
    verified = {}
    total = sum(min(len(v), max_per_channel) for v in matched.values())
    print(f"开始验证 {total} 个源（每个频道最多 {max_per_channel} 个）...")
    
    tasks = []
    for channel_name, sources in matched.items():
        # 只验证前N个源
        for url, orig_name, tvg_id, logo in sources[:max_per_channel]:
            tasks.append((channel_name, url, orig_name, tvg_id, logo))
    
    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {}
        for task in tasks:
            future = executor.submit(check_stream, task[1])
            future_map[future] = task
        
        for future in as_completed(future_map):
            completed += 1
            task = future_map[future]
            channel_name, url, orig_name, tvg_id, logo = task
            is_ok, latency = future.result()
            
            status = "✅" if is_ok else "❌"
            if completed % 20 == 0 or is_ok:
                print(f"  [{completed}/{total}] {status} {channel_name} ({latency}ms)")
            
            if is_ok:
                if channel_name not in verified:
                    verified[channel_name] = []
                verified[channel_name].append((url, latency, tvg_id, logo))
    
    # 每个频道按延迟排序
    for ch in verified:
        verified[ch].sort(key=lambda x: x[1])
    
    print(f"\n验证完成: {len(verified)}/{len(matched)} 个频道有可用源")
    return verified


def generate_m3u(verified):
    """生成M3U文件"""
    lines = ['#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"']
    
    # 按频道类别排序
    cctv_order = ["CCTV1", "CCTV2", "CCTV3", "CCTV4", "CCTV5", "CCTV5+", "CCTV6", "CCTV7", "CCTV8",
                  "CCTV9", "CCTV10", "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15", "CCTV16", "CCTV17"]
    weishi = [ch for ch in verified if ch not in cctv_order and ch not in ["金鹰卡通", "卡酷少儿", "炫动卡通", "优漫卡通"]]
    weishi.sort()
    qita = ["金鹰卡通", "卡酷少儿", "炫动卡通", "优漫卡通"]
    
    # 央视
    for ch in cctv_order:
        if ch in verified:
            url, latency, tvg_id, logo = verified[ch][0]
            logo_attr = f' tvg-logo="{logo}"' if logo else ""
            tvg_attr = f' tvg-id="{tvg_id}"' if tvg_id else ""
            lines.append(f'#EXTINF:-1 group-title="央视"{tvg_attr}{logo_attr},{ch}')
            lines.append(url)
    
    # 卫视
    for ch in weishi:
        if ch in verified:
            url, latency, tvg_id, logo = verified[ch][0]
            logo_attr = f' tvg-logo="{logo}"' if logo else ""
            tvg_attr = f' tvg-id="{tvg_id}"' if tvg_id else ""
            lines.append(f'#EXTINF:-1 group-title="卫视"{tvg_attr}{logo_attr},{ch}')
            lines.append(url)
    
    # 其他
    for ch in qita:
        if ch in verified:
            url, latency, tvg_id, logo = verified[ch][0]
            logo_attr = f' tvg-logo="{logo}"' if logo else ""
            tvg_attr = f' tvg-id="{tvg_id}"' if tvg_id else ""
            lines.append(f'#EXTINF:-1 group-title="少儿/卡通"{tvg_attr}{logo_attr},{ch}')
            lines.append(url)
    
    return "\n".join(lines)


def generate_stats(verified, matched):
    """生成统计信息"""
    stats = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_sources_collected": sum(len(v) for v in matched.values()),
        "channels_available": len(verified),
        "channels_target": len(TARGET_CHANNELS),
        "channels_missing": [ch for ch in TARGET_CHANNELS if ch not in verified],
        "channel_details": {}
    }
    for ch, sources in verified.items():
        stats["channel_details"][ch] = {
            "best_latency_ms": sources[0][1],
            "total_working_sources": len(sources)
        }
    return stats


def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 收集源
    all_entries = collect_all_sources()
    
    # 2. 匹配目标频道
    matched = match_target_channels(all_entries)
    
    # 3. 验证源
    verified = verify_sources_parallel(matched)
    
    # 4. 生成M3U
    m3u_content = generate_m3u(verified)
    m3u_path = os.path.join(output_dir, "iptv.m3u")
    with open(m3u_path, "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print(f"\n✅ M3U文件已生成: {m3u_path}")
    
    # 5. 生成统计
    stats = generate_stats(verified, matched)
    stats_path = os.path.join(output_dir, "stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"📊 统计信息: {stats_path}")
    
    # 6. 打印摘要
    print(f"\n{'='*40}")
    print(f"IPTV 聚合结果摘要")
    print(f"{'='*40}")
    print(f"目标频道: {len(TARGET_CHANNELS)} 个")
    print(f"可用频道: {len(verified)} 个")
    print(f"缺失频道: {len(stats['channels_missing'])} 个")
    if stats["channels_missing"]:
        print(f"缺失列表: {', '.join(stats['channels_missing'])}")
    print(f"{'='*40}")
    
    return 0 if len(verified) > 20 else 1


if __name__ == "__main__":
    sys.exit(main())
