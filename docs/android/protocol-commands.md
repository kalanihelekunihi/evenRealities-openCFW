# Even G2 Protocol — Command Enums (Android Extraction)

> All command type enums extracted from `even_android.apk` Dart AOT snapshot, 2026-03-14.
> These are the definitive protobuf enum values used in the BLE protocol.

## Service Command ID Enums

Each service has a `CommandId` enum defining its command types:

| Enum Name | Service | Notes |
|-----------|---------|-------|
| `eDashboardCommandId` | 0x01-20 | Dashboard |
| `eNotificationCommandId` | 0x02-20 | Notifications |
| `eTranslateCommandId` | 0x05-20 | Translation |
| `TelepromptCommandId` | 0x06-20 | Teleprompter |
| `eEvenAICommandId` | 0x07-20 | EvenAI |
| `ConversateCommandId` | 0x0B-20 | Conversate |
| `eQuicklistCommandId` | 0x0C-20 | Quicklist |
| `eHealthCommandId` | 0x0C-20 | Health (shared) |
| `g2_settingCommandId` | 0x0D-00 | G2 Settings |
| `eDevCfgCommandId` | 0x0D-20 | Device Config |
| `eOnboardingCommandId` | 0x10-20 | Onboarding |
| `eGlassesCaseCommandId` | 0x81-20 | Glasses Case |
| `eRingCommandId` | 0x91-20 | Ring Relay |
| `eTranscribeCommandId` | 0x??-?? | Transcribe (NEW) |

## Conversate Protocol (0x0B-20)

### Command Types
| Enum Value | Description |
|------------|-------------|
| `CONVERSATE_CONTROL` | Control command (start/stop/pause/resume) |
| `CONVERSATE_COMM_RESP` | Communication response/ACK |
| `CONVERSATE_HEART_BEAT` | Service-specific heartbeat |
| `CONVERSATE_STATUS_NOTIFY` | Status notification from glasses |
| `CONVERSATE_KEYPOINT_DATA` | Real-time key point extraction |
| `CONVERSATE_TAG_DATA` | Content tag/category data |
| `CONVERSATE_TAG_TRACKING_DATA` | Tag tracking over time |
| `CONVERSATE_TITLE_DATA` | Title/topic extraction |
| `CONVERSATE_TRANSCRIBE_DATA` | Transcription data |

### Control Commands (ConversateCtrlCmd)
- Start, Stop, Pause, Resume, Close (matching firmware enum NONE=0/START=1/PAUSE=2/RESUME=3/CLOSE=4/CONFIG=5)

### Error Codes
| Enum Value | Description |
|------------|-------------|
| `CONVERSATE_NONE` | No error |
| `CONVERSATE_SUCCESS` | Success |
| `CONVERSATE_ERR_NETWORK` | Network error |
| `CONVERSATE_ERR_FAIL` | General failure |

## Teleprompter Protocol (0x06-20)

### Command Types
| Enum Value | Description |
|------------|-------------|
| `TELEPROMPT_CONTROL` | Control command |
| `TELEPROMPT_COMM_RESP` | Communication response/ACK |
| `TELEPROMPT_HEART_BEAT` | Service-specific heartbeat |
| `TELEPROMPT_STATUS_NOTIFY` | Status notification |
| `TELEPROMPT_PAGE_DATA` | Page content data |
| `TELEPROMPT_PAGE_DATA_REQUEST` | Request page data |
| `TELEPROMPT_PAGE_AI_SYNC` | AI voice synchronization |
| `TELEPROMPT_PAGE_SCROLL_SYNC` | Scroll position sync |
| `TELEPROMPT_FILE_LIST` | File list response |
| `TELEPROMPT_FILE_LIST_REQUEST` | Request file list |
| `TELEPROMPT_FILE_SELECT` | Select file from glasses |

### Error Codes
| Enum Value | Description |
|------------|-------------|
| `TELEPROMPT_NONE` | No error |
| `TELEPROMPT_SUCCESS` | Success |
| `TELEPROMPT_ERR_FAIL` | General failure |
| `TELEPROMPT_ERR_CLOSED` | Session closed |
| `TELEPROMPT_ERR_REPEATED_MESSAGE` | Duplicate message |
| `TELEPROMPT_ERR_PD_DECODE_FAIL` | Page data decode failure |

## Translate Protocol (0x05-20)

### Command Types
| Enum Value | Description |
|------------|-------------|
| `TRANSLATE_CTRL` | Control command |
| `TRANSLATE_HEARTBEAT` | Service-specific heartbeat |
| `TRANSLATE_MODE_SWITCH` | Switch translation mode |
| `TRANSLATE_NOTIFY` | Status notification |
| `TRANSLATE_RESULT` | Translation result data |

## Transcribe Protocol (NEW)

### Command Types
| Enum Value | Description |
|------------|-------------|
| `TRANSCRIBE_CTRL` | Control command |
| `TRANSCRIBE_HEARTBEAT` | Service-specific heartbeat |
| `TRANSCRIBE_NOTIFY` | Status notification |
| `TRANSCRIBE_RESULT` | Transcription result |

## Notification Protocol (0x02-20)

### Command Types
| Enum Value | Description |
|------------|-------------|
| `NOTIFICATION_CTRL` | Notification control |
| `NOTIFICATION_COMM_RSP` | Communication response |
| `NOTIFICATION_IOS` | iOS notification format |
| `NOTIFICATION_JSON_WHITELIST` | JSON whitelist data |
| `NOTIFICATION_WHITELIST_CTRL` | Whitelist control command |

## EvenAI Protocol (0x07-20)

### Command Types
| Enum Value | Description |
|------------|-------------|
| `EVEN_AI_ENTER` | Enter EvenAI mode |
| `EVEN_AI_EXIT` | Exit EvenAI mode |
| `EVEN_AI_WAKE_UP` | Wake word detected |

## Dashboard/EvenHub Protocol (0xE0-20)

### EvenHub Commands (APP_REQUEST_*)
| Enum Value | Description |
|------------|-------------|
| `APP_REQUEST_START_UP` | Initialize/create startup page |
| `APP_REQUEST_CREATE_STARTUP_PAGE_PACKET` | Startup page creation |
| `APP_REQUEST_CREATE_PAGE_SUCCESS` | Page created successfully |
| `APP_REQUEST_HEARTBEAT_PACKET` | EvenHub heartbeat |
| `APP_REQUEST_UPGRADE_HEARTBEAT_PACKET_SUCCESS` | Heartbeat upgrade success |
| `APP_REQUEST_SHUTDOWN_PAGE_PACKET` | Shutdown/close page |
| `APP_REQUEST_REBUILD_PAGE_PACKET` | Rebuild/refresh page |
| `APP_REQUEST_REBUILD_PAGE_SUCCESS` | Rebuild success |
| `APP_REQUEST_REBUILD_PAGE_FAILD` | Rebuild failed (note: typo in original) |
| `APP_REQUEST_EXIT` | Exit EvenHub |
| `APP_REQUEST_SYNC_INFO` | Sync info request |
| `APP_REQUEST_CLEAR_ALL_DATA` | Clear all data |
| `APP_REQUEST_NEWS_INFO` | Request news data |
| `APP_REQUEST_NAVIGATION_COMPLETE` | Navigation completed |
| `APP_REQUEST_RECALCULATING_LOCATION_START` | Rerouting started |
| `APP_REQUEST_AUDIO_CTR_PACKET` | Audio control packet |
| `APP_REQUEST_AUDIO_CTR_SUCCESS` | Audio control success |
| `APP_REQUEST_AUDIO_CTR_FAILED` | Audio control failed |
| `APP_REQUEST_CREATE_INVAILD_CONTAINER` | Invalid container error (typo in original) |
| `APP_REQUEST_CREATE_OUTOFMEMORY_CONTAINER` | Out of memory error |
| `APP_REQUEST_CREATE_OVERSIZE_RESPONSE_CONTAINER` | Response too large error |

### EvenHub Data Commands (APP_SEND_* / APP_UPDATE_*)
| Enum Value | Description |
|------------|-------------|
| `APP_SEND_BASIC_INFO` | Send basic info to glasses |
| `APP_SEND_HEARTBEAT_CMD` | Send heartbeat command |
| `APP_SEND_MENU_INFO` | Send menu data |
| `APP_SEND_NEWS_DATA` | Send news content |
| `APP_SEND_MAX_MAP_FILE` | Send full map file |
| `APP_SNED_MINI_MAP_FILE` | Send mini map file (note: typo "SNED") |
| `APP_SEND_ERROR_INFO_MSG` | Send error message |
| `APP_UPDATE_TEXT_DATA_PACKET` | Update text data |
| `APP_UPDATE_IMAGE_RAW_DATA_PACKET` | Update image data |
| `APP_UPGRADE_TEXT_DATA_SUCCESS/FAILED` | Text data upgrade result |
| `APP_UPGRADE_IMAGE_RAW_DATA_SUCCESS/FAILED` | Image data upgrade result |
| `APP_UPGRADE_SHUTDOWN_SUCCESS/FAILED` | Shutdown result |

### EvenHub Response Codes
| Enum Value | Description |
|------------|-------------|
| `APP_RECEIVE` | Received |
| `APP_RECEIVED_SUCCESS` | Received successfully |
| `APP_RESPOND_SUCCESS` | Response success |
| `APP_RESPOND_PARAMETER_ERROR` | Parameter error |
| `APP_PARAMETER_ERROR` | Parameter error (alias) |
| `APP_RESPONSE_LOCATION_LIST` | Location list response |
| `APP_RESPONSE_LOCATION_NONE` | No location available |

### EvenHub Query/Set Commands
| Enum Value | Description |
|------------|-------------|
| `APP_REQUIRE_BASIC_SETTING` | Query basic settings |
| `APP_REQUIRE_BRIGHTNESS_INFO` | Query brightness info |
| `APP_INQUIRE_DASHBOARD_AUTO_CLOSE_VALUE` | Query auto-close timer |
| `APP_SET_DASHBOARD_AUTO_CLOSE_VALUE` | Set auto-close timer |

### Settings Commands (APP_Send_*)
| Enum Value | Description |
|------------|-------------|
| `APP_Send_Dominant_Hand` | Set dominant hand |
| `APP_Send_Gesture_Control` | Set gesture action |
| `APP_Send_Gesture_Control_List` | Set full gesture mapping |
| `APP_Send_Universe_Setting` | Set universal settings |
| `APP_Control_Device` | Device control command |

### Dashboard Response Codes
| Enum Value | Description |
|------------|-------------|
| `DASHBOARD_RECEIVED_SUCCESS` | Data received |
| `DASHBOARD_PARAMETER_ERROR` | Parameter error |
| `DASHBOARD_NEWS_VERSION_ERROR` | News version mismatch |

## File Transfer Protocol (EFS 0xC4/0xC5)

### Send Commands
| Enum Value | Description |
|------------|-------------|
| `EVEN_FILE_SERVICE_CMD_SEND_START` | Start file send |
| `EVEN_FILE_SERVICE_CMD_SEND_DATA` | Send file data chunk |
| `EVEN_FILE_SERVICE_CMD_SEND_RESULT_CHECK` | Verify send result |

### Export Commands
| Enum Value | Description |
|------------|-------------|
| `EVEN_FILE_SERVICE_CMD_EXPORT_START` | Start file export |
| `EVEN_FILE_SERVICE_CMD_EXPORT_DATA` | Export data chunk |
| `EVEN_FILE_SERVICE_CMD_EXPORT_RESULT_CHECK` | Verify export result |

### Response Codes
| Enum Value | Description |
|------------|-------------|
| `EVEN_FILE_SERVICE_RSP_SUCCESS` | Success |
| `EVEN_FILE_SERVICE_RSP_FAIL` | General failure |
| `EVEN_FILE_SERVICE_RSP_DATA_CRC_ERR` | CRC error |
| `EVEN_FILE_SERVICE_RSP_FLASH_WRITE_ERR` | Flash write error |
| `EVEN_FILE_SERVICE_RSP_NO_RESOURCES` | No resources |
| `EVEN_FILE_SERVICE_RSP_RESULT_CHECK_FAIL` | Result check failed |
| `EVEN_FILE_SERVICE_RSP_START_ERR` | Start error |
| `EVEN_FILE_SERVICE_RSP_TIMEOUT` | Timeout |

### UX IDs (Pipe Routing)
| Enum Value | Description |
|------------|-------------|
| `UX_EVEN_FILE_SERVICE_CMD_SEND_ID` | Send command pipe ID |
| `UX_EVEN_FILE_SERVICE_CMD_EXPORT_ID` | Export command pipe ID |
| `UX_EVEN_FILE_SERVICE_RAW_SEND_DATA_ID` | Raw send data pipe ID |
| `UX_EVEN_FILE_SERVICE_RAW_EXPORT_DATA_ID` | Raw export data pipe ID |

## OTA Protocol

### Transmit Phases
| Enum Value | Description |
|------------|-------------|
| `OTA_TRANSMIT_START` | OTA start (phase 1) |
| `OTA_TRANSMIT_INFORMATION` | OTA information (phase 2) |
| `OTA_TRANSMIT_FILE` | OTA file transfer (phase 3) |
| `OTA_TRANSMIT_RESULT_CHECK` | OTA result check (phase 4) |
| `OTA_TRANSMIT_NOTIFY` | OTA notification |

### Response Codes
| Enum Value | Description |
|------------|-------------|
| `OTA_RECV_RSP_SUCCESS` | Success |
| `OTA_RECV_RSP_FAIL` | General failure |
| `OTA_RECV_RSP_CRC_ERR` | CRC error |
| `OTA_RECV_RSP_FLASH_WRITE_ERR` | Flash write error |
| `OTA_RECV_RSP_NO_RESOURCES` | No resources |
| `OTA_RECV_RSP_CHECK_FAIL` | Check failed |
| `OTA_RECV_RSP_HEADER_ERR` | Header error |
| `OTA_RECV_RSP_PATH_ERR` | Path error |
| `OTA_RECV_RSP_TIMEOUT` | Timeout |
| `OTA_RECV_RSP_UPDATING` | Already updating |
| `OTA_RECV_RSP_SYS_RESTART` | System restart required |

## SyncInfo Protocol (NEW)

### Protobuf Messages
| Message | Description |
|---------|-------------|
| `sync_info_main_msg_ctx` | Main sync info message context |
| `sync_info_data_msg` | Sync data message |
| `APP_REQUEST_SYNC_INFO` | Sync info request command |
| `OS_NOTIFY_SYNC_INFO4` | OS notification for sync info |
| `SERVICE_SYNC_INFO_APP_ID` | App ID for sync info service |

## OS Notifications (Firmware → App)

| Event | Description |
|-------|-------------|
| `OS_NOTIFY_COMPASS_CALIBRATE_STRAT` | Compass calibration started |
| `OS_NOTIFY_COMPASS_CALIBRATE_COMPLETE` | Compass calibration completed |
| `OS_NOTIFY_COMPASS_CHANGED` | Compass heading changed |
| `OS_NOTIFY_EXIT` | Feature exit notification |
| `OS_NOTIFY_LOCATION_SELECTED` | Location selected on glasses |
| `OS_NOTIFY_MENU_STARTUP_REQUEST_LOCATION_LIST` | Menu requests location list |
| `OS_NOTIFY_REVIEW_CHANGED` | Review state changed |
| `OS_NOTIFY_SYNC_INFO4` | Sync info notification |

## Glasses Display Text Categories (86 strings)

The `os_*` string prefix indicates text shown on glasses display:

| Category | Count | Examples |
|----------|-------|---------|
| `os_dashboard_*` | ~30 | Calendar, health, news, quicklist, stocks, weather |
| `os_even_ai_*` | ~12 | Brightness, bluetooth, network, notifications |
| `os_conversate_*` | ~5 | Close, saved, topic summary |
| `os_translate_*` | ~3 | Start, end, unsupported language |
| `os_general_*` | ~5 | Bluetooth, confirmation, ring |
| `os_navigate_*` | ~3 | Arrival, rerouting |
| `os_teleprompt_*` | ~3 | Closed, complete |
