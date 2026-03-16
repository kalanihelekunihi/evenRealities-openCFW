# Even G2 Protocol — Complete Protobuf Message Catalog

> Definitive catalog of all protobuf message types extracted from Dart AOT snapshot hash-based class grouping, 2026-03-14.
> Updated with oneof field structures and UI App IDs from deep protobuf field extraction.

## Method

Dart protobuf generated classes share a library hash suffix (`_@NNNNNNNN`). By grouping all classes with the same hash, we can identify every message type within each service's proto file.

## UI/UX App IDs (Service Routing)

Each service has a unique App ID used for BLE routing:

| Service | App ID Constant |
|---------|----------------|
| Dashboard | `UI_BACKGROUND_DASHBOARD_APP_ID` |
| EvenHub | `UI_BACKGROUND_EVENHUB_APP_ID` |
| Navigation | `UI_BACKGROUND_NAVIGATION_ID` |
| EvenAI | `UI_FOREGROUND_EVEN_AI_ID` |
| Menu | `UI_FOREGROUND_MEUN_ID` |
| Notification | `UI_FOREGROUND_NOTIFICATION_ID` |
| System Alert | `UI_FOREGROUND_SYSTEM_ALERT_APP_ID` |
| System Close | `UI_FOREGROUND_SYSTEM_CLOSE_APP_ID` |
| Conversate | `UI_CONVERSATE_APP_ID` |
| Teleprompter | `UI_TELEPROMPT_APP_ID` |
| Translate | `UI_TRANSLATE_APP_ID` |
| Transcribe | `UI_TRANSCRIBE_APP_ID` |
| Health | `UI_HEALTH_APP_ID` |
| Quicklist | `UI_QUICKLIST_APP_ID` |
| Onboarding | `UI_ONBOARDING_APP_ID` |
| Logger | `UI_LOGGER_APP_ID` |
| Settings | `UI_SETTING_APP_ID` |
| DevConfig | `UX_DEVICE_SETTINGS_APP_ID` |
| GlassesCase | `UX_GLASSES_CASE_APP_ID` |
| Ring | `UX_RING_DATA_RELAY_ID` |
| ModuleConfigure | `SERVICE_MODULE_CONFIGURE_APP_ID` |
| SyncInfo | `SERVICE_SYNC_INFO_APP_ID` |
| File Send | `UX_EVEN_FILE_SERVICE_CMD_SEND_ID` |
| File Export | `UX_EVEN_FILE_SERVICE_CMD_EXPORT_ID` |
| OTA Cmd | `UX_OTA_TRANSMIT_CMD_ID` |
| OTA Data | `UX_OTA_TRANSMIT_RAW_DATA_ID` |

## G2 Settings Service (0x0D-00) — Hash @1424153617

### App → Device Messages
| Message | Description |
|---------|-------------|
| `G2SettingPackage` | Main settings wrapper |
| `APP_Send_Dominant_Hand` | Set left/right hand dominance |
| `APP_Send_Gesture_Control` | Set individual gesture action |
| `APP_Send_Gesture_Control_List` | Set complete gesture mapping |
| `APP_Send_Universe_Setting` | Set universal settings |
| `APP_Control_Device` | Device control command |
| `Wear_Detection_Setting` | Configure wear detection |

### Device → App Messages
| Message | Description |
|---------|-------------|
| `DeviceReceiveInfoFromAPP` | Device received info from app |
| `DeviceReceiveRequestFromAPP` | Device received request from app |
| `DeviceReceive_Brightness` | Brightness setting received |
| `DeviceReceive_Silent_Mode_Setting` | Silent mode setting received |
| `DeviceReceive_Advanced_Setting` | Advanced settings received |
| `DeviceReceive_Head_UP_Setting` | Head-up display setting received |
| `DeviceReceive_X_Coordinate` | X coordinate setting received |
| `DeviceReceive_Y_Coordinate` | Y coordinate setting received |
| `DeviceReceive_APP_PAGE` | App page setting received |
| `DeviceSendInfoToAPP` | Device sends info to app |

### Response Messages
| Message | Description |
|---------|-------------|
| `App_Respond_To_Device` | App response to device |
| `Device_Respond_To_App` | Device response to app |

## Dashboard/EvenHub Service (0x01-20 / 0xE0-20) — Hash @1430512574

### Core Messages
| Message | Description |
|---------|-------------|
| `DashboardDataPackage` | Main wrapper |
| `DashboardContent` | Content definition |
| `DashboardDisplaySetting` | Display configuration |
| `DashboardMainPageState` | Page state |

### App → Device
| Message | Description |
|---------|-------------|
| `DashboardReceiveFromApp` | Device receives from app |
| `AppRequest` | Generic app request |
| `AppRequestDeviceNewsInfo` | Request news from device |
| `AppResetClearAllDataMsg` | Clear all data command |
| `AppRespondToDashboard` | App responds to dashboard |
| `AppSendNewsData` | Send news articles |

### Device → App
| Message | Description |
|---------|-------------|
| `DashboardRespondToApp` | Dashboard response |
| `DashboardSendToApp` | Dashboard sends to app |
| `DeviceNotifyNewsEvent` | News event notification |
| `DeviceRequestNewsUpgrade` | Device requests news update |
| `DeviceResponseClearAllDataMsg` | Clear data response |
| `DeviceResponseNewData` | New data available |
| `DeviceResponseNewsInfo` | News info response |
| `RequestNewsFifoCountCmd` | Request news FIFO count |
| `ResponseNewsFifoMsg` | News FIFO response |

### Widget Render Messages (r* prefix = render)
| Message | Description |
|---------|-------------|
| `rNewsWidget` | Rendered news widget |
| `rScheduleWidget` | Rendered schedule/calendar widget |
| `rStatusComponent` | Rendered status component |
| `rStockWidget` | Rendered stock widget |
| `rWeatherStatus` | Rendered weather status |
| `rWidgetComponent` | Generic rendered widget component |

### Widget Sync Messages (s* prefix = sync)
| Message | Description |
|---------|-------------|
| `sNewsWidget` | News widget sync |
| `sNewsWidgetApplyNews` | Apply news to widget |
| `sNewsWidgetSync` | News widget sync command |
| `sNotificationStatus` | Notification status sync |
| `sPageStateSync` | Page state synchronization |
| `sPowerStatus` | Power status sync |
| `sScheduleWidget` | Schedule widget sync |
| `sStatusComponent` | Status component sync |
| `sStockWidget` | Stock widget sync |
| `sWidgetComponent` | Generic widget sync |

### Content Types
| Message | Description |
|---------|-------------|
| `News` | News article data |
| `Schedule` | Calendar/schedule entry |
| `Stock` | Stock data |

### Page States
| Message | Description |
|---------|-------------|
| `CalendarExpandedPageState` | Calendar expanded view |
| `HealthExpandedPageState` | Health expanded view |
| `NewsExpandedPageState` | News expanded view |
| `QuicklistExpandedPageState` | Quicklist expanded view |
| `StockExpandedPageState` | Stock expanded view |

## EvenAI Service (0x07-20) — Hash @1417414150

**EvenAIDataPackage oneof commandData fields:**
- `control` → `EvenAIControl`
- `askInfo` → `EvenAIAskInfo`
- `analyseInfo` → `EvenAIAnalyseInfo`
- `replyInfo` → `EvenAIReplyInfo`
- `skillInfo` → `EvenAISkillInfo`
- `promptInfo` → `EvenAIPromptInfo`
- `config` → `EvenAIConfig`
- `heartbeat` → `EvenAIHeartbeat`
- `vadInfo` → `EvenAIVADInfo`
- `commResp` → `EvenAICommRsp`
- `event` → `EvenAIEvent`

**Additional fields:** `vadStatus` (eEvenAIVADStatus), `skillId` (eEvenAISkill), `promptType` (eEvenAIPrompt), `errorCode`, `eventId`, `eventParam`

**Sub-enums:** `eEvenAIEvent`, `eEvenAIPrompt`, `eEvenAISkill`, `eEvenAIStatus`, `eEvenAIVADStatus`, `EvenAISentiment`

| Message | Description |
|---------|-------------|
| `EvenAIDataPackage` | Main wrapper |
| `EvenAIControl` | Control command (enter/exit/wakeup) |
| `EvenAIHeartbeat` | Service heartbeat |
| `EvenAICommRsp` | Communication response |
| `EvenAIAskInfo` | Ask/query information (type 3) |
| `EvenAIAnalyseInfo` | Analysis information (type 4) |
| `EvenAIReplyInfo` | Reply information (type 5) |
| `EvenAISkillInfo` | Skill command (type 6) |
| `EvenAIPromptInfo` | Prompt information (type 7) |
| `EvenAIEvent` | Event notification (type 8) |
| `EvenAIConfig` | Configuration (type 10) |
| `EvenAIVADInfo` | Voice Activity Detection info (type 2) |

## Conversate Service (0x0B-20) — Hash @1937268313

| Message | Description |
|---------|-------------|
| `ConversateDataPackage` | Main wrapper |
| `ConversateControl` | Control (start/stop/pause/resume/close) |
| `ConversateHeartBeat` | Service heartbeat |
| `ConversateCommResp` | Communication response |
| `ConversateStatusNotify` | Status notification |
| `ConversateSettings` | Configuration |
| `ConversateKeypointData` | Real-time key point extraction |
| `ConversateTagData` | Content tagging |
| `ConversateTagTrackingData` | Tag tracking over time |
| `ConversateTitleData` | Title/topic extraction |
| `ConversateTranscribeData` | Transcription data |

## Teleprompter Service (0x06-20) — Hash @1453303095

| Message | Description |
|---------|-------------|
| `TelepromptDataPackage` | Main wrapper |
| `TelepromptControl` | Control command |
| `TelepromptHeartBeat` | Service heartbeat |
| `TelepromptCommResp` | Communication response |
| `TelepromptStatusNotify` | Status notification |
| `TelepromptSetting` | Configuration |
| `TelepromptPageData` | Page content data |
| `TelepromptPageDataRequest` | Request page content |
| `TelepromptAISync` | AI voice synchronization |
| `TelepromptScrollSync` | Scroll position sync |
| `TelepromptFileInfo` | File metadata |
| `TelepromptFileList` | File catalog |
| `TelepromptFileListRequest` | Request file catalog |
| `TelepromptFileSelect` | Select file |

## Translate Service (0x05-20) — Hash @1461417037

| Message | Description |
|---------|-------------|
| `TranslateDataPackage` | Main wrapper |
| `TranslateControl` | Control command |
| `TranslateHeartBeat` | Service heartbeat |
| `TranslateResp` | Response/ACK |
| `TranslateResult` | Translation result |
| `TranslateModeSwitch` | Mode switch command |
| `TranslateNotify` | Status notification |

## Transcribe Service (NEW) — Hash @2428442198

| Message | Description |
|---------|-------------|
| `TranscribeDataPackage` | Main wrapper |
| `TranscribeControl` | Control command |
| `TranscribeHeartBeat` | Service heartbeat |
| `TranscribeResp` | Response/ACK |
| `TranscribeResult` | Transcription result |
| `TranscribeNotify` | Status notification |

## Health Service (0x0C-20 shared) — Hash @1432255604

| Message | Description |
|---------|-------------|
| `HealthDataPackage` | Main wrapper |
| `HealthSingleData` | Single metric data point |
| `HealthSingleHighlight` | Single metric highlight |
| `HealthMultData` | Multiple metric data |
| `HealthMultHighlight` | Multiple metric highlights |

## Quicklist Service (0x0C-20 shared) — Hash @1446323404

| Message | Description |
|---------|-------------|
| `QuicklistDataPackage` | Main wrapper |
| `QuicklistItem` | Individual task item |
| `QuicklistMultItems` | Multiple items batch |
| `QuicklistEvent` | Quicklist event |

## Notification Service (0x02-20) — Hash @1440261884

| Message | Description |
|---------|-------------|
| `NotificationDataPackage` | Main wrapper |
| `NotificationControl` | Control command |
| `NotificationCommRsp` | Communication response |
| `NotificationIOS` | iOS-format notification (used on both platforms!) |
| `NotificationWhitelistCtrl` | Whitelist management |

## Navigation Service (0x08-20) — Hash @1438067439

| Message | Description |
|---------|-------------|
| `navigation_main_msg_ctx` | Main navigation context |
| `basic_info_msg` | Basic navigation info (distance, time, street) |
| `compass_info_msg` | Compass heading data |
| `extend_info_msg` | Extended navigation info |
| `view_info_msg` | View/display info |
| `max_map_msg` | Full-size map image |
| `mini_map_msg` | Mini map image |
| `LocationList_msg` | Location list |
| `os_select_location_msg` | Location selection from glasses |

## Ring Service (0x91-20) — Hash @1448371976

| Message | Description |
|---------|-------------|
| `RingDataPackage` | Main wrapper |
| `RingEvent` | Ring event data |
| `RingRawData` | Raw ring data |

## GlassesCase Service (0x81-20) — Hash @1425496902

| Message | Description |
|---------|-------------|
| `GlassesCaseDataPackage` | Main wrapper |
| `GlassesCaseInfo` | Case info (SOC, charging, lid, in-case) |

## Onboarding Service (0x10-20) — Hash @1427321442

| Message | Description |
|---------|-------------|
| `OnboardingDataPackage` | Main wrapper |
| `OnboardingConfig` | Configuration |
| `OnboardingEvent` | Onboarding event |
| `OnboardingHeartbeat` | Service heartbeat |

## DevConfig Service (0x0D-20) — Hash @1420360820

| Message | Description |
|---------|-------------|
| `DevCfgDataPackage` | Main wrapper |
| `DevCfgCmdException` | Command exception/error |

## SyncInfo Service (NEW) — Hash @1450088238

| Message | Description |
|---------|-------------|
| `sync_info_main_msg_ctx` | Main sync info context |
| `sync_info_data_msg` | Sync data message |

## Logger Service (0x0F-20)

| Message | Description |
|---------|-------------|
| `logger_main_msg_ctx` | Main logger context |

## ModuleConfigure Service (0x20-20)

| Message | Description |
|---------|-------------|
| `module_configure_main_msg_ctx` | Main module configure context |

## Menu Service (0x03-20)

| Message | Description |
|---------|-------------|
| `MenuInfoSend` | Send menu info |
| `ResponseMenuInfo` | Menu info response |
| `Menu_Item_Ctx` | Menu item context |

## EvenHub Container Protocol (0xE0-20) — Deep Structure

The EvenHub uses a container-based display model:

### Container Commands (App → Glasses)
| Message | Description |
|---------|-------------|
| `CreateStartUpPageContainer` | Create startup display |
| `RebuildPageContainer` | Rebuild display page |
| `ShutDownContaniner` | Shutdown display (typo in original) |
| `HeartBeatPacket` | EvenHub keepalive |
| `TextContainerUpgrade` | Update text content |
| `ImageRawDataUpdate` | Update image content |
| `AudioCtrCmd` / `AudioResCmd` | Audio control/response |
| `SendDeviceEvent` | Device event relay |
| `PipeRoleChange` | Pipe switching |

### Container Properties
| Message | Description |
|---------|-------------|
| `ImageContainerProperty` | Image display properties |
| `TextContainerProperty` | Text display properties |
| `ListContainerProperty` | List display properties |
| `List_ItemContainerProperty` | List item properties |

### Container Events
| Message | Description |
|---------|-------------|
| `CommonDevicePrivateEvent` | Private device event |
| `CommonDevicePrivateSystemEvent` | System-level event |
| `Sys_ItemEvent` | System item event |
| `Text_ItemEvent` | Text item event |
| `List_ItemEvent` | List item event |

### Container Responses (Glasses → App)
| Message | Description |
|---------|-------------|
| `ResponseCreateStartupCmd` | Startup creation response |
| `ResponseHeartBeatCmd` | Heartbeat response |
| `ResponseImageRawDataCmd` | Image data response |
| `ResponseRebuildCmd` | Rebuild response |
| `ResponseShutDownCmd` | Shutdown response |
| `ResponseTextUpgradeCmd` | Text upgrade response |

### OS_RESPONSE Constants (Glasses → App)
- `OS_RESPONSE_CREATE_STARTUP_PAGE_PACKET`
- `OS_RESPONSE_REBUILD_PAGE_PACKET`
- `OS_RESPONSE_SHUTDOWN_PAGE_PACKET`
- `OS_RESPONSE_HEARTBEAT_PACKET`
- `OS_RESPONSE_TEXT_DATA_PACKET`
- `OS_RESPONSE_IMAGE_RAW_DATA_PACKET`
- `OS_RESPONSE_AUDIO_CTR_PACKET`
- `OS_RESPONSE_MENU_INFO`

### Page Types
- `PAGE_TYPE_DASHBOARD_MAIN`
- `PAGE_TYPE_CALENDAR_EXPANDED`
- `PAGE_TYPE_HEALTH_EXPANDED`
- `PAGE_TYPE_NEWS_EXPANDED`
- `PAGE_TYPE_QUICKLIST_EXPANDED`
- `PAGE_TYPE_STOCK_EXPANDED`
- `PAGE_TYPE_UNKNOWN`

## DeviceInfo Protocol (0x09-xx) — Hash @2379168945

| Message | Description |
|---------|-------------|
| `DeviceInfo` | Main container |
| `DeviceInfoValue` | Key/value pairs |
| `ALSInfo` | Ambient light sensor data |
| `HeadAngle` | Head tilt angle |
| `BleMac` | BLE MAC address |
| `SnInfo` | Serial number |
| `Mode` | Current device mode |

## Auth/DevPairManager Protocol (0x80-xx) — Hash @2427051248

| Message | Description |
|---------|-------------|
| `AuthMgr` | Authentication manager |
| `BleConnectParam` | Connection parameters |
| `DisconnectInfo` | Disconnect notification |
| `PipeRoleChange` | Pipe role switching |
| `RingInfo` | Ring information |
| `UnpairInfo` | Unpair notification |

## DevSettings Protocol (0x0A-20) — Hash @1421012352

| Message | Description |
|---------|-------------|
| `AudControl` | Audio control |
| `BaseConnHeartBeat` | Connection heartbeat |
| `QuickRestart` | Quick restart command |
| `RestoreFactory` | Factory reset |
| `TimeSync` | Time synchronization |

## Summary Statistics

| Service | Message Count | New vs iOS |
|---------|:---:|:---:|
| Dashboard/EvenHub | 42 | +30 new |
| G2 Settings | 19 | +15 new |
| Teleprompter | 14 | +8 new |
| EvenAI | 12 | +5 new |
| Conversate | 11 | +7 new |
| Navigation | 9 | +3 new |
| Translate | 7 | +4 new |
| Transcribe | 6 | ALL new |
| Health | 5 | +3 new |
| Notification | 5 | +2 new |
| Quicklist | 4 | +1 new |
| Ring | 3 | +1 new |
| Onboarding | 4 | +2 new |
| SyncInfo | 2 | ALL new |
| GlassesCase | 2 | +0 |
| DevConfig | 2 | +1 new |
| Menu | 3 | +1 new |
| Logger | 1 | +0 |
| ModuleConfigure | 1 | +0 |
| **TOTAL** | **152** | **+83 new** |
