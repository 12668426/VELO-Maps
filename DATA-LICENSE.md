# 数据来源、许可与覆盖

© OpenStreetMap contributors。本仓库 Release 中的 OSM 衍生数据库依据 [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/) 发布，不附加限制该数据库再使用的条款；详 [OpenStreetMap copyright](https://www.openstreetmap.org/copyright)。使用时保留署名与许可证链接。

统一 `.vmap` 是 ZIP；机器可读衍生数据库在 `map.vmp/road_store.sqlite` 与 `routing.vht/tiles/**/*.gph`，可使用标准 ZIP 工具解包。VMP 还包含公共道路/建筑及图输入数据，无个人地址、导航轨迹或用户 Rules。公共数据与私有 App/编译器源码的许可边界不同。

淮南试点来源：[Geofabrik 安徽 extract](https://download.geofabrik.de/asia/china/anhui.html)，OSM 数据时间 2026-10-03T20:20:50Z；原输入 SHA-256 `b5fcd64cf16e425a36a35b97bebaad7af71eb0ad13c3c000c625ba044345c43c`。

实际裁取 WGS84 外接矩形：经度 116.3526607…117.2093797，纬度 31.9021797…33.0073139。它不是精确淮南行政多边形，也不是安徽全省。路图范围不表示所有路段均准许摩托车通行；不提供实时道路限制完整性保证。

包内 VMP schema 2 / compiler 0.5.2；VHT schema 1 / native Valhalla 3.6.3（28 graph tiles）；outer `.vmap` schema 1。source PBF 是编译输入，不能直接安装到 App 或 ESP32。每个新增地区必须独立记录版本/来源/覆盖/许可，不能沿用本段替代。

目录及校验工具另以 MIT 许可发布，见 [LICENSE](LICENSE)；数据库始终为上述 ODbL 数据许可。
