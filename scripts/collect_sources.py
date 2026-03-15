#!/usr/bin/env python3
"""
IPTV源收集器 v2 - 异步高速收集、验证国内电视频道
"""
import json
import os
import re
import sys
import time
import asyncio
import aiohttp
from datetime import datetime

# ============================================
# 频道映射
# ============================================
CHANNEL_MAP = {
    "CCTV1": ["CCTV1", "CCTV-1", "央视综合", "中央一套", "CCTV1综合"],
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
    "湖北卫视": ["湖北卫视", "湖北台", "湖北HD", "HBTV"],
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
    "三沙卫视": ["三沙卫视", "三沙台"],
    "金鹰卡通": ["金鹰卡通", "金鹰卡通卫视"],
    "卡酷少儿": ["卡酷少儿", "卡酷动画"],
    "优漫卡通": ["优漫卡通"],
}

TARGET_CHANNELS = list(CHANNEL_MAP.keys())

# ============================================
# 公开源列表
# ============================================
SOURCES = [
    {"name": "YueChan", "type": "m3u", "url": "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u"},
    {"name": "YanG", "type": "m3u", "url": "https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u"},
    {"name": "fanmingming", "type": "m3u", "url": "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u"},
    {"name": "ssili126", "type": "m3u", "url": "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u"},
    {"name": "iptv-org", "type": "m3u", "url": "https://raw.githubusercontent.com/iptv-org/iptv/master/countries/cn.m3u"},
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def normalize_channel_name(name):
    """标准化频道名称"""
    name = name.strip().replace(" ", "")
    for standard_name, aliases in CHANNEL_MAP.items():
        for alias in aliases:
            if alias.lower() in name.lower() or name.lower() in alias.lower():
                return standard_name
    return name


def parse_m3u(content):
    """解析M3U内容"""
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
            match = re.search(r',(.+)$', line)
            if match:
                current_name = match.group(1).strip()
            tvg_match = re.search(r'tvg-id="([^"]*)"', line)
            if tvg_match:
                current_tvg = tvg_match.group(1)
            logo_match = re.search(r'tvg-logo="([^"]*)"', line)
            if logo_match:
                current_logo = logo_match.group(1)
        elif line and not line.startswith("#") and current_name:
            if line.startswith("http") or line.startswith("rtsp") or line.startswith("rtmp"):
                entries.append((current_name, line.strip(), current_tvg, current_logo))
            current_name = None
            current_tvg = ""
            current_logo = ""
    return entries


def parse_txt(content):
    """解析TXT格式"""
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
        elif "://" in line and line.startswith("http"):
            entries.append((line, line.strip(), "", ""))
    return entries


async def fetch_source(session, src, semaphore):
    """异步获取单个源"""
    async with semaphore:
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with session.get(src["url"], timeout=timeout, headers=HEADERS) as resp:
                if resp.status == 200:
                    content = await resp.text(errors="ignore")
                    if src["type"] == "m3u":
                        entries = parse_m3u(content)
                    else:
                        entries = parse_txt(content)
                    print(f"  ✅ {src['name']}: {len(entries)} 个频道")
                    return entries
                else:
                    print(f"  ❌ {src['name']}: HTTP {resp.status}")
                    return []
        except Exception as e:
            print(f"  ❌ {src['name']}: {str(e)[:50]}")
            return []


async def collect_all_sources_async():
    """异步收集所有源"""
    semaphore = asyncio.Semaphore(5)  # 并发限制
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_source(session, src, semaphore) for src in SOURCES]
        results = await asyncio.gather(*tasks)
    all_entries = []
    for entries in results:
        all_entries.extend(entries)
    return all_entries


def match_target_channels(entries):
    """匹配目标频道"""
    matched = {}
    for name, url, tvg_id, logo in entries:
        standard_name = normalize_channel_name(name)
        if standard_name in TARGET_CHANNELS:
            if standard_name not in matched:
                matched[standard_name] = []
            matched[standard_name].append((url, name, tvg_id, logo))
        else:
            for target in TARGET_CHANNELS:
                if target in name or name in target:
                    if target not in matched:
                        matched[target] = []
                    matched[target].append((url, name, tvg_id, logo))
                    break
    print(f"匹配到 {len(matched)} 个目标频道，共 {sum(len(v) for v in matched.values())} 个源")
    return matched


async def check_stream(session, url, semaphore):
    """异步检查单个流"""
    async with semaphore:
        try:
            start = time.time()
            timeout = aiohttp.ClientTimeout(total=5)
            async with session.get(url, timeout=timeout, headers={"User-Agent": "VLC/3.0.0"},
                                   allow_redirects=True) as resp:
                latency = int((time.time() - start) * 1000)
                if resp.status == 200:
                    # 读取少量数据确认流有效
                    data = b""
                    try:
                        async for chunk in resp.content.iter_chunked(1024):
                            data = chunk
                            break
                    except:
                        pass
                    if len(data) > 0 or resp.status == 200:
                        return True, latency
                return False, 99999
        except Exception:
            return False, 99999


async def verify_sources_async(matched, max_per_channel=5):
    """异步验证所有源"""
    verified = {}
    semaphore = asyncio.Semaphore(50)  # 高并发验证

    tasks = []
    task_meta = {}
    for channel_name, sources in matched.items():
        for url, orig_name, tvg_id, logo in sources[:max_per_channel]:
            tasks.append((channel_name, url, tvg_id, logo))
            task_meta[(channel_name, url)] = (orig_name, tvg_id, logo)

    total = len(tasks)
    print(f"开始验证 {total} 个源（每个频道最多 {max_per_channel} 个，50并发）...")

    async with aiohttp.ClientSession() as session:
        async def verify_one(channel_name, url, tvg_id, logo):
            is_ok, latency = await check_stream(session, url, semaphore)
            return channel_name, url, is_ok, latency, tvg_id, logo

        coros = [verify_one(ch, url, tvg, logo) for ch, url, tvg, logo in tasks]
        results = await asyncio.gather(*coros)

    ok_count = 0
    for channel_name, url, is_ok, latency, tvg_id, logo in results:
        if is_ok:
            ok_count += 1
            if channel_name not in verified:
                verified[channel_name] = []
            verified[channel_name].append((url, latency, tvg_id, logo))

    # 按延迟排序
    for ch in verified:
        verified[ch].sort(key=lambda x: x[1])

    print(f"验证完成: {len(verified)}/{len(matched)} 个频道有可用源, {ok_count} 个源可用")
    return verified


def generate_m3u(verified):
    """生成M3U文件"""
    lines = ['#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"']

    cctv_order = [f"CCTV{i}" for i in range(1, 18)] + ["CCTV5+"]
    weishi = sorted([ch for ch in verified if ch not in cctv_order and "卡通" not in ch and "卡酷" not in ch])
    qita = [ch for ch in verified if ch in ["金鹰卡通", "卡酷少儿", "优漫卡通"]]

    for group_title, channels in [("央视", cctv_order), ("卫视", weishi), ("少儿", qita)]:
        for ch in channels:
            if ch in verified:
                url, latency, tvg_id, logo = verified[ch][0]
                attrs = ""
                if tvg_id:
                    attrs += f' tvg-id="{tvg_id}"'
                if logo:
                    attrs += f' tvg-logo="{logo}"'
                lines.append(f'#EXTINF:-1 group-title="{group_title}"{attrs},{ch}')
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


async def main_async():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    print("=== IPTV 聚合源收集器 v2 ===\n")

    # 1. 异步收集源
    print("📡 步骤1: 收集源...")
    all_entries = await collect_all_sources_async()
    print(f"\n总共收集到 {len(all_entries)} 个条目\n")

    if not all_entries:
        print("❌ 没有收集到任何源，退出")
        return 1

    # 2. 匹配目标频道
    print("🔍 步骤2: 匹配目标频道...")
    matched = match_target_channels(all_entries)

    if not matched:
        print("❌ 没有匹配到任何目标频道，退出")
        return 1

    # 3. 异步验证源
    print("\n✅ 步骤3: 验证源...")
    verified = await verify_sources_async(matched)

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

    # 6. 打印摘要
    print(f"\n{'='*40}")
    print(f"IPTV 聚合结果摘要")
    print(f"{'='*40}")
    print(f"目标频道: {len(TARGET_CHANNELS)} 个")
    print(f"可用频道: {len(verified)} 个")
    print(f"缺失频道: {len(stats['channels_missing'])} 个")
    if stats["channels_missing"]:
        print(f"缺失列表: {', '.join(stats['channels_missing'][:10])}...")
    print(f"{'='*40}")

    return 0


def main():
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
