/* Android notification service, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\message_notify\service_android_notify.c.
 * Native 0x48e494..0x48e84f (literal pool 0x48e850..0x48e8d3). The registry callback
 * android_notify_ancc_forward 0x48e484 of the same file lives in
 * system/registry-callback/registry_callback_48e484.c.
 *
 * The phone sends Android notifications as JSON {"android_notification":{...}}. The parsed
 * record shares the ANCC notification cache layout (0x2fc bytes, profileAnccGetActive);
 * whitelisted apps (type 2 or 3) are forwarded to the peer through SendDataToBoth with
 * sync application id 0x101. */
#include <stdint.h>
#include <stddef.h>

#define ANDROID_SYNC_APP_ID 0x101u
#define ANDROID_WHITELIST_NOTIFY 2u
#define ANDROID_WHITELIST_NOTIFY_ALT 3u

/* cJSON item (upstream cJSON layout). */
typedef struct cjson_item {
    struct cjson_item *next;  /* +0x00 */
    struct cjson_item *prev;  /* +0x04 */
    struct cjson_item *child; /* +0x08 */
    int32_t type;             /* +0x0c */
    char *valuestring;        /* +0x10 */
    int32_t valueint;         /* +0x14 */
} cjson_item_t;

/* ANCC/Android notification record, 0x2fc bytes. */
typedef struct {
    uint32_t msg_id;            /* +0x000 "msg_id" */
    uint8_t type;               /* +0x004 "type" */
    uint8_t reserved_005[3];
    char app_identifier[64];    /* +0x008 "app_identifier" (63 copied) */
    char display_name[32];      /* +0x048 "display_name" (31 copied) */
    char title[64];             /* +0x068 "title" (63 copied) */
    char subtitle[64];          /* +0x0a8 "subtitle" (63 copied) */
    char message[512];          /* +0x0e8 "message" (511 copied) */
    char date[16];              /* +0x2e8 "date" (15 copied) */
    uint8_t action;             /* +0x2f8 "action" */
    uint8_t reserved_2f9[3];
} android_notification_t;
_Static_assert(offsetof(android_notification_t, display_name) == 0x48u, "display_name");
_Static_assert(offsetof(android_notification_t, message) == 0xe8u, "message");
_Static_assert(offsetof(android_notification_t, action) == 0x2f8u, "action");
_Static_assert(sizeof(android_notification_t) == 0x2fcu, "notification record");

extern cjson_item_t *cJSON_Parse(const char *value);                                 /* 0x4d7f7e */
extern cjson_item_t *cJSON_GetObjectItem(const cjson_item_t *object, const char *name); /* 0x4d83aa */
extern void cJSON_Delete(cjson_item_t *item);                                         /* 0x4d79fa */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len);      /* strncpy 0x44b5a0 */
extern uint8_t service_ancc_state_byte0_get(void);                                     /* 0x4972a2 */
extern android_notification_t *profileAnccGetActive(void);                             /* 0x4bf8ac */
extern uint8_t audio_ble_ancc_whitelist_type_4d67b8(const uint8_t *id); /* SVC_IsOnWhitelistByIdentifier */
extern int32_t audio_ble_send_status_message(uint32_t application, const uint8_t *data, uint32_t length,
                                             uint32_t correlation); /* SendDataToBoth 0x464d1c */
extern uint32_t audio_log_flags(void);                                                /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);       /* 0x43ce9e */

void _androidSendCompleteNotificationMsg(const android_notification_t *record, uint32_t length);
void _androidParseNotification(const char *json, android_notification_t *out);
void SVC_ANDROID_ParseNotification(const char *json);

static const char module_tag[] = "svc.android_notify"; /* ROM 0x782e0c */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\message_notify\\service_android_notify.c"; /* ROM 0x6de554 */
static const char sync_fn[] = "_rxSyncEventCallback"; /* ROM 0x77b2b4 */
static const char sync_status[] = "SyncStatus = %d"; /* ROM 0x7886c0 */
static const char sync_status_short[] = "[svc.android_notify]SyncStatus = %d"; /* ROM 0x7590fc */
static const char sync_error[] =
    "!!!!!!!!!!!!!!!Dual-Glasses Communication ERROR = %d!!!!!!!!!!!!!!!"; /* ROM 0x705380 */
static const char sync_error_short[] =
    "[svc.android_notify]!!!!!!!!!!!!!!!Dual-Glasses Communication ERROR = %d!!!!!!!!!!!!!!!"; /* ROM 0x6e4ab8 */
static const char send_fn[] = "_androidSendCompleteNotificationMsg"; /* ROM 0x759120 */
static const char send_msg[] = "android Send Complete Notification Msg"; /* ROM 0x74d7dc */
static const char send_msg_short[] = "[svc.android_notify]android Send Complete Notification Msg"; /* ROM 0x718220 */
static const char parse_fn[] = "_androidParseNotification"; /* ROM 0x770bbc */
static const char root_error[] = "error root JSON NODE!"; /* ROM 0x77b2cc */
static const char root_error_short[] = "[svc.android_notify]error root JSON NODE!"; /* ROM 0x742a44 */
static const char node_missing[] = "NOT FOUND Android_msg JSON NODE!"; /* ROM 0x759144 */
static const char node_missing_short[] = "[svc.android_notify]NOT FOUND Android_msg JSON NODE!"; /* ROM 0x722548 */
static const char key_root[] = "android_notification"; /* ROM 0x77b2e4 */
static const char key_app_identifier[] = "app_identifier"; /* ROM 0x7886d0 */
static const char key_msg_id[] = "msg_id"; /* ROM 0x78e4bc */
static const char key_action[] = "action"; /* ROM 0x78e4c4 */
static const char key_type[] = "type"; /* ROM 0x78e4cc */
static const char key_title[] = "title"; /* ROM 0x78e4d4 */
static const char key_subtitle[] = "subtitle"; /* ROM 0x78be10 */
static const char key_message[] = "message"; /* ROM 0x78e4dc */
static const char key_date[] = "date"; /* ROM 0x78e4e4 */
static const char key_display_name[] = "display_name"; /* ROM 0x7886e0 */
static const char svc_fn[] = "SVC_ANDROID_ParseNotification"; /* ROM 0x764890 */
static const char whitelist_result[] = "Whitelist check result: appType=%d"; /* ROM 0x759168 */
static const char whitelist_result_short[] =
    "[svc.android_notify]Whitelist check result: appType=%d"; /* ROM 0x722580 */
static const char on_whitelist[] = "Android app(%s) name(%s) is on whitelist"; /* ROM 0x742a70 */
static const char on_whitelist_short[] =
    "[svc.android_notify]Android app(%s) name(%s) is on whitelist"; /* ROM 0x70e924 */
static const char off_whitelist[] = "Android app(%s) name(%s) not on whitelist, ignore!!!!"; /* ROM 0x7225b8 */
static const char off_whitelist_short[] =
    "[svc.android_notify]Android app(%s) name(%s) not on whitelist, ignore!!!!"; /* ROM 0x6f5bb0 */

#define LOG_ON() ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))

/* SendDataToBoth completion callback. _rxSyncEventCallback is a shared stock name
 * (0x48e494, 0x4bed0e, ...): file-local here. */
static int32_t _rxSyncEventCallback(int32_t status)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, sync_fn, 0x28u, sync_status, status);
    if (LOG_ON())
        (void)compress_log_output(0x10400000u, sync_status_short, sync_status_short, status);
    if (status != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, sync_fn, 0x2au, sync_error, status);
        if (LOG_ON())
            (void)compress_log_output(0x04400000u, sync_error_short, sync_error_short, status);
    }
    return status;
}

void _androidSendCompleteNotificationMsg(const android_notification_t *record, uint32_t length)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, send_fn, 0x31u, send_msg);
    if (LOG_ON())
        (void)compress_log_output(0x10000000u, send_msg_short, send_msg_short);
    (void)audio_ble_send_status_message(ANDROID_SYNC_APP_ID, (const uint8_t *)record, (uint16_t)length,
                                        (uint32_t)(uintptr_t)_rxSyncEventCallback);
}

void _androidParseNotification(const char *json, android_notification_t *out)
{
    cjson_item_t *root = cJSON_Parse(json);

    if (root == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, parse_fn, 0x39u, root_error);
        if (LOG_ON())
            (void)compress_log_output(0x04000000u, root_error_short, root_error_short);
        return;
    }
    cjson_item_t *node = cJSON_GetObjectItem(root, key_root);
    if (node == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, parse_fn, 0x3fu, node_missing);
        if (LOG_ON())
            (void)compress_log_output(0x04000000u, node_missing_short, node_missing_short);
        cJSON_Delete(root);
        return;
    }
    cjson_item_t *app_identifier = cJSON_GetObjectItem(node, key_app_identifier);
    cjson_item_t *msg_id = cJSON_GetObjectItem(node, key_msg_id);
    cjson_item_t *action = cJSON_GetObjectItem(node, key_action);
    cjson_item_t *type = cJSON_GetObjectItem(node, key_type);
    cjson_item_t *title = cJSON_GetObjectItem(node, key_title);
    cjson_item_t *subtitle = cJSON_GetObjectItem(node, key_subtitle);
    cjson_item_t *message = cJSON_GetObjectItem(node, key_message);
    cjson_item_t *date = cJSON_GetObjectItem(node, key_date);
    cjson_item_t *display_name = cJSON_GetObjectItem(node, key_display_name);

    (void)aeabi_memset_43c0e4(out, sizeof(*out), 0);
    if (msg_id != NULL)
        out->msg_id = (uint32_t)msg_id->valueint;
    if (action != NULL)
        out->action = (uint8_t)action->valueint;
    if (type != NULL)
        out->type = (uint8_t)type->valueint;
    if (app_identifier != NULL)
        (void)audio_settings_copy_text(out->app_identifier, app_identifier->valuestring,
                                       sizeof(out->app_identifier) - 1u);
    if (title != NULL)
        (void)audio_settings_copy_text(out->title, title->valuestring, sizeof(out->title) - 1u);
    if (message != NULL)
        (void)audio_settings_copy_text(out->message, message->valuestring, sizeof(out->message) - 1u);
    if (subtitle != NULL)
        (void)audio_settings_copy_text(out->subtitle, subtitle->valuestring, sizeof(out->subtitle) - 1u);
    if (date != NULL)
        (void)audio_settings_copy_text(out->date, date->valuestring, sizeof(out->date) - 1u);
    if (display_name != NULL)
        (void)audio_settings_copy_text(out->display_name, display_name->valuestring,
                                       sizeof(out->display_name) - 1u);
    cJSON_Delete(root);
}

/* Parse into the active ANCC record, then forward it to the peer only when whitelisted. */
void SVC_ANDROID_ParseNotification(const char *json)
{
    if (service_ancc_state_byte0_get() == 0u)
        return;
    android_notification_t *record = profileAnccGetActive();
    _androidParseNotification(json, record);
    uint8_t app_type = audio_ble_ancc_whitelist_type_4d67b8((const uint8_t *)record->app_identifier);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, svc_fn, 0x89u, whitelist_result, app_type);
    if (LOG_ON())
        (void)compress_log_output(0x10400000u, whitelist_result_short, whitelist_result_short, app_type);
    if (app_type == ANDROID_WHITELIST_NOTIFY || app_type == ANDROID_WHITELIST_NOTIFY_ALT) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module_tag, source_file, svc_fn, 0x8eu, on_whitelist,
                               record->app_identifier, record->display_name);
        if (LOG_ON())
            (void)compress_log_output(0x0c800000u, on_whitelist_short, on_whitelist_short,
                                      record->app_identifier, record->display_name);
        _androidSendCompleteNotificationMsg(record, sizeof(*record));
    } else {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module_tag, source_file, svc_fn, 0x92u, off_whitelist,
                               record->app_identifier, record->display_name);
        if (LOG_ON())
            (void)compress_log_output(0x0c800000u, off_whitelist_short, off_whitelist_short,
                                      record->app_identifier, record->display_name);
    }
}
