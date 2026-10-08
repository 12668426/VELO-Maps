# VELO 离线地图下载库

只发布公共 OSM 衍生地图/算路数据、下载目录和校验工具；不包含 VELO 产品源码、密钥、个人地址、Rules 或设备日志。

## 当前可用性

- 全国 34 个省级条目：**准备中**，尚未生成完整省级包，不提供虚构下载链接。
- 安徽淮南市裁取包：已通过既有包验证；公开下载回读完成后才加入 `pilotPackages`。
- App 自动下载入口尚未接入。本仓库创建不代表手机软件已能直接下载。
- 淮南试点不是安徽全省；市级包不会改名冒充省级包。

## 分发方式

小型 JSON 目录放 Git；大型 `.vmap` 文件放 [Releases](https://github.com/12668426/VELO-Maps/releases)。统一包内含 `map.vmp` 和 `routing.vht`，用户只下载/安装一次。它是 VELO 自有道路与离线算路数据，不是高德普通/卫星离线图片缓存。

目录入口：[catalog.json](https://raw.githubusercontent.com/12668426/VELO-Maps/main/catalog.json)。未就绪条目 `status=preparing`；仅校验并公开回读的版本才 `available`，包含真实 bytes、SHA-256、固定版本 URL、来源时间与覆盖范围。

离线数据存在不等于摩托车在每条道路合法；禁限行仍需本地规则与核验。跨省联合路由尚未验证。

## 发布顺序

1. 本地校验统一包及其内部身份/hash/公共数据文件白名单。
2. 提交公共发布说明；新建固定 tag 的 Release，不覆盖旧资产。
3. 匿名实际下载，校验 bytes、SHA-256 和包内部数据。
4. 更新目录到 available，再校验/提交/推送目录。

GitHub 下载在弱网/不可达时可能失败；未来 App 应明确提示和允许重试，保留旧地图，不假装离线包已安装。无手机验证时不标手机 Gate 通过。

## 本地目录测试

Python 3 标准库即可：`python3 -m unittest discover -s tests -v`，`python3 validate_catalog.py catalog.json`。

## 数据许可

© OpenStreetMap contributors。地图衍生数据库按 [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) 分发，详 [DATA-LICENSE.md](DATA-LICENSE.md)。下载包内提供机器可读 Road Store 与 native 图数据库；公共数据授权不扩展到私有 VELO 产品代码。
