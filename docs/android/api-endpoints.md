# Even G2 Cloud API Endpoints (Android App Analysis)

Comprehensive documentation of all cloud API endpoints and services extracted from reverse engineering the Even Android application. This supplements the iOS-derived API knowledge with Android-specific findings.

---

## Base URLs

| Environment    | URL                                    | Notes                        |
|----------------|----------------------------------------|------------------------------|
| Production     | `https://api2.evenreal.co`             | Primary API server           |
| Pre-production | `https://pre-g2.evenreal.co`           | Pre-release testing          |
| Staging        | `https://api2.ev3n.co`                 | Note: `ev3n` not `even`      |
| CDN Primary    | `https://cdn.evenreal.co`              | Firmware, assets             |
| CDN Secondary  | `https://cdn2.evenreal.co`             | Fallback/load-balanced CDN   |
| Development    | `http://192.168.2.113:8888`            | Internal dev server (no TLS) |
| Web Portal     | `https://evenapp.evenrealities.com`    | User-facing web interface    |

---

## Custom Headers

| Header                      | Purpose          |
|-----------------------------|------------------|
| `evenrealities-trace-id`    | Request tracing / distributed trace correlation |

---

## API Service Extensions

The Android app organizes API calls into Dart extension classes on a shared `ApiService` base. Each extension groups related endpoints.

### Authentication & User (`ApiServiceLoginExt`, `ApiServiceUserExt`)

| Endpoint               | Description                              | Notes                                  |
|------------------------|------------------------------------------|----------------------------------------|
| `login6`               | User login                               | Version 6 of login API (not generic)   |
| `register`             | User registration                        |                                        |
| `requestVerifyCode`    | Request SMS/email verification code      |                                        |
| `checkCode`            | Verify submitted code                    |                                        |
| `checkPassword`        | Password validation                      |                                        |
| `checkRegister`        | Check registration status                |                                        |
| `resetPassword`        | Password reset flow                      |                                        |
| `userProfile`          | Get user profile                         |                                        |
| `logout`               | Logout / invalidate session              |                                        |
| `deleteAccount`        | Account deletion (GDPR/regulatory)       |                                        |
| `updateUserProfile`    | Update profile fields                    |                                        |
| `uploadAvatar`         | Avatar image upload                      |                                        |
| `getUserSetting`       | Get user settings                        |                                        |
| `updateUserSettings`   | Update user settings                     |                                        |
| `getUserHealth`        | Get user health data                     |                                        |
| `updateUserHealth`     | Update user health data                  |                                        |
| `getPrivacyUrls`       | Privacy policy / ToS URLs                |                                        |
| `findMyDeviceAndTerminal` | Find device and terminal info         |                                        |
| `inboxList`            | List inbox messages                      |                                        |
| `inboxUnreadCount`     | Get unread message count                 |                                        |
| `inboxMarkAsRead`      | Mark inbox message(s) as read            |                                        |
| `inboxDelete`          | Delete inbox message(s)                  |                                        |

### Device Management (`ApiServiceUserExt`)

| Endpoint               | Description                              | Notes                                  |
|------------------------|------------------------------------------|----------------------------------------|
| `bindDevice`           | Bind device to account                   | Uses `sn` parameter (not `device_sn`)  |
| `unbindDevice`         | Unbind device from account               |                                        |
| `checkDeviceIsBind`    | Check if device is bound                 |                                        |
| `isSnInBlacklist`      | Check serial number against blacklist    | Blacklisting system for banned devices |
| `setDeviceRemark`      | Set device nickname/label                |                                        |
| `updateGlassesConfig`  | Update glasses configuration             |                                        |
| `unbindTerminal`       | Unbind terminal (phone) from account     |                                        |
| `updateIosAppList`     | Update iOS notification app whitelist    | iOS-specific but called from Android too |

### Firmware (`ApiServiceCommonExt`)

| Endpoint               | Description                              | Notes                                  |
|------------------------|------------------------------------------|----------------------------------------|
| `checkAppVersion`      | Check for app updates                    |                                        |
| `checkFirmware`        | Firmware update check (legacy)           | Older API path                         |
| `checkLatestFirmware`  | Latest firmware check                    | v2 API: `GET /v2/g/check_latest_firmware` |
| `syncFirmware`         | Report firmware version to server        |                                        |

### AI & Chat (`ApiServiceEvenAiExt`)

| Endpoint               | Description                              | Notes                                  |
|------------------------|------------------------------------------|----------------------------------------|
| `requestAiChat`        | Send AI chat request                     |                                        |
| `getAiChatHistory`     | Retrieve chat history                    |                                        |
| `markAiChatMessage`    | Mark/flag a chat message                 |                                        |
| `clearChatHistory`     | Clear all chat history                   |                                        |

### Conversate Background Documents (`ApiServiceConverseBackgroundExt`)

These endpoints manage context documents that can be uploaded for Conversate AI sessions.

| Endpoint                      | Description                         | Notes                                  |
|-------------------------------|-------------------------------------|----------------------------------------|
| `createConverseBackground`    | Upload background document          | Context file for AI conversations      |
| `deleteConverseBackground`    | Delete a background document        |                                        |
| `getConverseBackgroundList`   | List uploaded backgrounds           |                                        |
| `getConverseBackgroundStatus` | Check document processing status    | Async processing after upload          |
| `updateConverseBackground`    | Update an existing background       |                                        |

### Health (`ApiServiceHealthExt`)

| Endpoint                 | Description                            | Notes                                  |
|--------------------------|----------------------------------------|----------------------------------------|
| `getHealthLatestData`    | Get latest health readings             |                                        |
| `postHealthDailyData`    | Upload daily health summary            |                                        |
| `queryMetricWindow`      | Query single metric for time window    |                                        |
| `batchQueryMetricWindow` | Batch query multiple metrics at once   | Not found in iOS analysis              |
| `getHealthExport`        | Export health data                     |                                        |
| `getGoMorePKey`          | GoMore health integration key          | Third-party fitness integration        |

### Translation (`ApiServiceTranslateExt`)

| Endpoint                     | Description                          | Notes                                  |
|------------------------------|--------------------------------------|----------------------------------------|
| `getASRConfig`               | Get ASR provider configuration       | Azure/Soniox settings                  |
| `createTranslateSession`     | Create a new translation session     |                                        |
| `queryTranslateSession`      | Query session data/results           |                                        |
| `updateTranslateHistory`     | Update translation history entry     |                                        |
| `deleteTranslateHistory`     | Delete single history entry          |                                        |
| `deleteTranslateHistoryBatch`| Batch delete history entries         |                                        |
| `getTranslateAiSummary`      | AI-generated summary of translation  | Not found in iOS analysis              |

### Common (`ApiServiceCommonExt`)

| Endpoint          | Description                              | Notes                                  |
|-------------------|------------------------------------------|----------------------------------------|
| `getUserPrefs`    | Get user preferences                     |                                        |
| `setUserPrefs`    | Update user preferences                  |                                        |
| `getRingNv`       | Get R1 Ring NV (non-volatile) data       |                                        |
| `uploadRingNv`    | Upload R1 Ring NV data                   |                                        |

### Settings (`unit_setting_http_helper`)

| Endpoint          | Description                              | Notes                                  |
|-------------------|------------------------------------------|----------------------------------------|
| Unit settings     | Metric/imperial, date format, temperature | Managed via dedicated helper class     |

### Onboarding (`ApiServiceOnboardExt`)

| Endpoint                   | Description                          | Notes                                  |
|----------------------------|--------------------------------------|----------------------------------------|
| `postOnboardFlagFinished`  | Mark onboarding as complete          |                                        |

### Logging (`ApiServiceLogExt`)

| Endpoint                   | Description                          | Notes                                  |
|----------------------------|--------------------------------------|----------------------------------------|
| `submitFeedbackWithLog`    | Submit user feedback with device logs |                                       |

### Dashboard (`dashboard_http_helper`)

| Endpoint          | Description                              | Notes                                  |
|-------------------|------------------------------------------|----------------------------------------|
| Dashboard sync    | Dashboard configuration sync             | News, weather, stock, calendar settings |

### ASR Configuration (`asr_config_http_helper`)

| Endpoint          | Description                              | Notes                                  |
|-------------------|------------------------------------------|----------------------------------------|
| ASR config        | ASR provider selection and configuration | Provider-specific parameters           |

---

## API Models

Located in `even/common/api/models/` in the Android source.

### User & Auth
- `UserInfo` -- Core user identity
- `UserLogin` -- Login request/response
- `UserProfile` -- Extended profile data
- `UserSettings` -- User settings
- `UserPrefs` -- User preferences
- `UserBalance` -- Account balance/credits
- `UserActions` -- User action history
- `UserHealth` -- Health data model
- `LoginTerminal` -- Terminal/phone binding info

### Device
- `DeviceOtaInfo` -- OTA firmware info
- `MyDevices` -- Bound devices list
- `GlassesLenseInfo` -- Lens/glasses details

### AI & Chat
- `AiAgentSetting` -- AI agent configuration
- `AiChatEntity` -- Chat session entity
- `AiChatHistoryEntity` -- Chat history container
- `AiChatItemEntity` -- Individual chat message
- `AiCmdEntity` -- AI command entity
- `AiContentEntity` -- AI content/response entity

### Dashboard & Config
- `DashboardSetting` -- Dashboard layout and widget settings
- `ServiceConfig` -- Server-provided service configuration
- `RegionModel` -- Regional settings/locale

### Translation
- `TranslationProviderData` -- ASR/translation provider configuration

### App & Platform
- `AppUpdate` -- App version/update info
- `AppPrivacy` -- Privacy policy metadata

### Conversate
- `ConverseBackgroundResponse` -- Background document response

### Health
- `HealthModuleLastData` -- Latest health module readings
- `MonthlyUsed` -- Monthly usage statistics

### EvenHub (App Store)
- `HotAppInfo` -- Individual app listing
- `HotAppList` -- App store listings

### Social & Messaging
- `ReferFriend` -- Referral system
- `MsgBubble` -- Message bubble display
- `InboxMsgRequest` -- Inbox message request
- `SimpleResultModel` -- Generic API result wrapper

---

## WebSocket

| Service    | Implementation                                 | Notes                                  |
|------------|-------------------------------------------------|----------------------------------------|
| Conversate | `websocket_manager.dart` (conversate package)   | Live session data streaming            |
| General    | `wss://socket.evenreal.co`                      | WebSocket endpoint (from iOS analysis) |

---

## Network Infrastructure

### HTTP Client
- **Library**: Dio (Dart HTTP client)
- **Package**: `even_core/network`

### Interceptors
| Interceptor                     | File                               | Purpose                           |
|---------------------------------|------------------------------------|-----------------------------------|
| Auth interceptor                | `auth_interceptor.dart`            | Injects auth tokens into requests |
| Login expiry interceptor        | `login_expired_interceptor.dart`   | Handles token expiry and refresh  |

### Security Utilities
| Utility                  | File                          | Purpose                              |
|--------------------------|-------------------------------|--------------------------------------|
| Request signing          | `signature_util.dart`         | Request signature generation         |
| Encryption               | `encrypt_ext.dart`            | Payload encryption utilities         |
| Certificate pinning      | `even_certificate_util.dart`  | SSL certificate pinning              |

---

## Findings Not Present in iOS Analysis

These endpoints and details were discovered exclusively through Android app analysis:

1. **`login6`** -- The login API is explicitly versioned at v6. The iOS analysis only referenced a generic "login" endpoint.
2. **Conversate background documents** -- Full CRUD for uploading context files that feed into Conversate AI sessions (`createConverseBackground`, `getConverseBackgroundStatus`, etc.).
3. **`getTranslateAiSummary`** -- AI-generated summaries of translation sessions. Not observed in iOS code.
4. **`batchQueryMetricWindow`** -- Batch health metric queries (single call for multiple metrics). iOS uses individual queries.
5. **`getGoMorePKey`** -- GoMore third-party health/fitness integration key.
6. **`isSnInBlacklist`** -- Serial number blacklisting system for banning specific devices.
7. **`api2.ev3n.co`** -- Previously undocumented staging domain (note the `ev3n` spelling).
8. **`192.168.2.113:8888`** -- Internal development server IP exposed in the production app code.

---

## Complete Route Table (81 routes)

All routes under base URL `https://api2.evenreal.co`, extracted from Dart AOT snapshot 2026-03-14.

### Authentication & Account (10)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/login` | POST | User login (v6 internally) |
| `/v2/g/register` | POST | User registration |
| `/v2/g/send_code` | POST | Send verification code |
| `/v2/g/pre_check_code` | POST | Pre-check verification code |
| `/v2/g/check_password` | POST | Validate password |
| `/v2/g/check_reg` | GET | Check registration status |
| `/v2/g/reset_passwd` | POST | Password reset |
| `/v2/g/account_logout` | POST | Logout |
| `/v2/g/account_del` | POST | Delete account |
| `/v2/g/user_info` | GET | Get user info |

### User Profile & Settings (8)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/set_profile` | POST | Update user profile |
| `/v2/g/upload_avatar` | POST | Upload avatar image |
| `/v2/g/user_settings` | GET | Get user settings |
| `/v2/g/update_set` | POST | Update user settings |
| `/v2/g/get_user_prefs` | GET | Get user preferences |
| `/v2/g/set_user_prefs` | POST | Set user preferences |
| `/v2/g/set_on_boarded` | POST | Mark onboarding complete |
| `/v2/g/get_privacy_urls` | GET | Get privacy policy URLs |

### Device Management (9)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/bind_device` | POST | Bind device (uses `sn` param) |
| `/v2/g/unbind_device` | POST | Unbind device |
| `/v2/g/check_bind` | GET | Check device binding status |
| `/v2/g/list_devices` | GET | List user's devices |
| `/v2/g/set_device_remark` | POST | Set device nickname |
| `/v2/g/update_glasses_settings` | POST | Update glasses configuration |
| `/v2/g/unbind_terminal` | POST | Unbind login terminal |
| `/v2/g/update_ios_app_list` | POST | Update iOS notification app list |
| `/v2/g/is_sn_in_blacklist` | GET | Check serial number blacklist |

### Firmware (4)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/check_app` | GET | Check app version for update |
| `/v2/g/check_firmware` | GET | Check firmware (legacy) |
| `/v2/g/check_latest_firmware` | GET | Check latest firmware (v2) |
| `/v2/g/func_conf` | GET | Get function configuration |

### Ring NV Data (3)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/get_nv` | GET | Get R1 Ring NV data |
| `/v2/g/get_nv?sn=` | GET | Get NV data by serial number |
| `/v2/g/upload_nv` | POST | Upload ring NV data |

### ASR Configuration (1)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/asr_sconf` | GET | Get ASR service configuration |

### Jarvis AI (17)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/jarvis/chat` | POST | AI chat request |
| `/v2/g/jarvis/message/list` | GET | List AI messages |
| `/v2/g/jarvis/message/sentiment` | POST | Message sentiment analysis |
| `/v2/g/jarvis/session/action/delete` | POST | Delete AI session |
| `/v2/g/jarvis/conversate/ws` | WS | **WebSocket** for live Conversate |
| `/v2/g/jarvis/conversate/list` | GET | List Conversate sessions |
| `/v2/g/jarvis/conversate/detail` | GET | Get session detail |
| `/v2/g/jarvis/conversate/messages` | GET | Get session messages |
| `/v2/g/jarvis/conversate/update` | POST | Update session |
| `/v2/g/jarvis/conversate/finish` | POST | Finish/close session |
| `/v2/g/jarvis/conversate/remove` | POST | Delete session |
| `/v2/g/jarvis/conversate/background/create` | POST | Upload background document |
| `/v2/g/jarvis/conversate/background/list` | GET | List background documents |
| `/v2/g/jarvis/conversate/background/status` | GET | Background doc processing status |
| `/v2/g/jarvis/conversate/background/update` | POST | Update background document |
| `/v2/g/jarvis/conversate/background/remove` | POST | Delete background document |
| `/v2/g/jarvis/app_log/report` | POST | Report app log to Jarvis |

### Translation (5)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/translate_create` | POST | Create translation session |
| `/v2/g/translate_get` | GET | Get translation session |
| `/v2/g/translate_update` | POST | Update translation history |
| `/v2/g/translate_delete` | POST | Delete translation history |
| `/v2/g/translate_ai_summary` | POST | AI summary of translation |

### Health (8)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/health/get_info` | GET | Get health info |
| `/v2/g/health/update_info` | POST | Update health info |
| `/v2/g/health/get_latest_data` | GET | Get latest health data |
| `/v2/g/health/push` | POST | Push daily health data |
| `/v2/g/health/query_window` | GET | Query metric for time window |
| `/v2/g/health/batch_query_window` | GET | Batch query multiple metrics |
| `/v2/g/health/export` | GET | Export health data |
| `/v2/g/health/get_pkey` | GET | Get GoMore platform key |

### Inbox/Messaging (4)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/inbox/list` | GET | List inbox messages |
| `/v2/g/inbox/unread_count` | GET | Get unread count |
| `/v2/g/inbox/mark_as_read` | POST | Mark message as read |
| `/v2/g/inbox/delete` | POST | Delete inbox message |

### News (5)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/news_list` | GET | Get news articles |
| `/v2/g/news_categories` | GET | Get news categories |
| `/v2/g/news_sources` | GET | Get news sources |
| `/v2/g/news_favorites_settings` | GET | Get news favorites settings |
| `/v2/g/news_favorites_settings_save` | POST | Save news favorites settings |

### Stocks (6)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/stock_tickers` | GET | Search stock tickers |
| `/v2/g/stock_intraday` | GET | Get intraday stock data |
| `/v2/g/stock_favorite_list` | GET | List favorite stocks |
| `/v2/g/stock_favorite_create` | POST | Add favorite stock |
| `/v2/g/stock_favorite_del` | POST | Remove favorite stock |
| `/v2/g/stock_favorite_updateT` | POST | Update favorite stock |

### Feedback (1)
| Route | Method | Description |
|-------|--------|-------------|
| `/v2/g/filelogs/feedback` | POST | Submit feedback with log files |

---

## Cross-Reference

- iOS API routes: `Sources/EvenG2Shortcuts/G2FirmwareAPIClient.swift` (16 routes in `G2APIRoutes`)
- iOS API models: `Sources/EvenG2Shortcuts/G2FirmwareModels.swift`
- API security assessment: [api-security-assessment.md](api-security-assessment.md)
- API signing details: [api-signing.md](api-signing.md)
- Firmware update pipeline: [../firmware/firmware-updates.md](../firmware/firmware-updates.md)
