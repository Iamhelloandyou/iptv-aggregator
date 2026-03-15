# 📺 IPTV 聚合源

自动收集、验证、更新国内电视频道源，每小时自动检查失效源并替换。

## 🔗 M3U 播放地址

将以下地址添加到 IPTV 播放器中使用：

```
https://iamhelloandyou.github.io/iptv-aggregator/output/iptv.m3u
```

## 📺 频道列表

- **央视**：CCTV1-17（含CCTV5+）
- **卫视**：湖南、浙江、东方、江苏、北京、广东、深圳等32个省级卫视
- **其他**：金鹰卡通、卡酷少儿、炫动卡通、优漫卡通

## 🛠 技术架构

- 从 12+ 公开源仓库收集频道
- 自动验证流可用性，测量延迟
- 选择最优源生成 M3U 文件
- GitHub Actions 每小时自动更新

## 📱 推荐播放器

| 平台 | 播放器 |
|------|--------|
| iOS / Apple TV | IPTV Pro / CloudStream |
| Android | TiviMate / OTT Navigator |
| Windows / Mac | VLC / PotPlayer / IINA |
| 智能电视 | TiviMate / 当贝播放器 |

## 🔄 手动更新

前往 [Actions](https://github.com/Iamhelloandyou/iptv-aggregator/actions) 页面，点击 "Run workflow" 手动触发更新。
