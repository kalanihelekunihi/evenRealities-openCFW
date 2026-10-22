/* Notification whitelist service, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\message_notify\service_whitelist.c.
 * Native 0x4d58d8..0x4d6a5b (minus SVC_IsOnWhitelistByIdentifier 0x4d67b8 and
 * the CRC cache getter 0x4d6a20, which live elsewhere in g2/src) plus
 * SVC_WhitelistManagerInit 0x4d6a5c..0x4d6abf; literal pools 0x4d5918..0x4d592f,
 * 0x4d631c..0x4d635f, 0x4d6770..0x4d67b7, 0x4d6a40..0x4d6a5b, 0x4d6ac0..0x4d6ba7.
 *
 * The phone writes user/notify_whitelist.json, e.g.
 *   {"call_enable":true,"msg_enable":true,"calendar_enable":false,
 *    "ios_mail_enable":false,
 *    "app":{"enable":true,"list":[{"id":"com.x.y","name":"X"}, ...]}}
 * It is parsed into the 8002-byte record at RAM 0x20054718 (at most 100 apps).
 * After a successful parse the CRC-32C of the raw file is cached for
 * APP_PbTxEncodeNotifWhitelistChk (0x4d76cc). */
#include <stdint.h>
#include <stddef.h>

#define WHITELIST_MAX_APPS 100u
#define WHITELIST_SHARED_BUFFER_LIMIT 0x2137u /* files below this use the shared buffer */
#define CJSON_TRUE 2                          /* cJSON_True type bit */

enum {
    WL_FLAG_CALL = 0x01u,     /* "call_enable" */
    WL_FLAG_MSG = 0x02u,      /* "msg_enable" (SMS) */
    WL_FLAG_MAIL = 0x04u,     /* "ios_mail_enable" */
    WL_FLAG_CALENDAR = 0x08u, /* "calendar_enable" */
    WL_FLAG_APP = 0x10u,      /* "app"."enable" */
};

typedef struct {
    char id[64];   /* +0x00 package / bundle identifier, 63 copied */
    char name[16]; /* +0x40 display name, 15 copied */
} g2_whitelist_app_t;
_Static_assert(sizeof(g2_whitelist_app_t) == 0x50u, "stock listAppInfo row");

typedef struct {
    uint8_t flags;  /* +0x0 WL_FLAG_* */
    uint8_t count;  /* +0x1 rows reported by the JSON list (clamped to 100) */
    g2_whitelist_app_t apps[WHITELIST_MAX_APPS]; /* +0x2 */
} g2_app_whitelist_info_t;
_Static_assert(sizeof(g2_app_whitelist_info_t) == 0x1f42u, "MAX_WHITE_LIST_BUF_LEN + 1");

/* Upstream cJSON item (v1.7.x layout). */
typedef struct g2_cjson {
    struct g2_cjson *next;  /* +0x00 */
    struct g2_cjson *prev;  /* +0x04 */
    struct g2_cjson *child; /* +0x08 */
    int32_t type;           /* +0x0c */
    char *valuestring;      /* +0x10 */
    int32_t valueint;       /* +0x14 */
} g2_cjson_t;

extern uint8_t audio_ble_whitelist_info[];                /* RAM 0x20054718, _g_appWhiteListInfo */
extern uint8_t audio_message_notify_crc_valid_2007501b;   /* RAM 0x2007501b */
extern uint32_t audio_message_notify_cached_crc_200749a4; /* RAM 0x200749a4 */

extern uint32_t audio_log_flags(void);                                       /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *path,
                               const char *function, uint32_t line, const char *format, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t mask, const char *format, const char *compact, ...); /* 0x43ce9e */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);  /* 0x43c0e4 */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */
extern void *file_open(const char *path, const char *mode);                  /* 0x474550 */
extern int32_t file_close(void *file);                                       /* 0x4745f4 */
extern uint32_t file_read(void *buffer, uint32_t size, uint32_t count, void *file); /* 0x474634 */
extern int32_t file_seek(void *file, int32_t offset, int32_t origin);        /* 0x474814 */
extern int32_t file_tell(void *file);                                        /* 0x474870 */
extern void *file_heap_allocate(uint32_t size);                              /* 0x474cd2 */
extern void file_heap_free(void *ptr);                                       /* 0x474d16 */
extern uint8_t *svc_android_notify_buffer_48e0a8(void);  /* shared buffer RAM 0x20354c78 */
extern void file_crc32c_update_47cbc4(const uint8_t *data, uint32_t length, uint32_t *crc);
extern g2_cjson_t *cJSON_Parse(const char *value);                           /* 0x4d7f7e */
extern void cJSON_Delete(g2_cjson_t *item);                                  /* 0x4d79fa */
extern g2_cjson_t *cJSON_GetObjectItem(const g2_cjson_t *object, const char *name); /* 0x4d83aa */
extern int32_t cJSON_IsArray(const g2_cjson_t *item);                        /* 0x4d83bc */
extern int32_t cJSON_GetArraySize(const g2_cjson_t *array);                  /* 0x4d830c */
extern g2_cjson_t *cJSON_GetArrayItem(const g2_cjson_t *array, int32_t index); /* 0x4d8344 */

#define WL_INFO ((g2_app_whitelist_info_t *)(void *)audio_ble_whitelist_info)

static const char module[] = "svc.whitelist"; /* ROM 0x788f90 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\message_notify\\service_whitelist.c"; /* ROM 0x6e51f0 */
static const char fn_parse_json[] = "_parseJsonWhitelistToStruct"; /* ROM 0x7719f4 */
static const char fn_print[] = "_printAppWhiteListInfo";          /* ROM 0x77bd4c */
static const char fn_parse_fs[] = "_parseWhiteListFromFS";         /* ROM 0x77bd94 */
static const char fn_init[] = "SVC_WhitelistManagerInit";          /* ROM 0x771a9c */
static const char whitelist_path[] = "user/notify_whitelist.json"; /* ROM 0x771ab8 */

static const char key_call[] = "call_enable";         /* ROM 0x78c0a4 */
static const char key_msg[] = "msg_enable";           /* ROM 0x78c0b0 */
static const char key_calendar[] = "calendar_enable"; /* ROM 0x788fb0 */
static const char key_mail[] = "ios_mail_enable";     /* ROM 0x788fc0 */
static const char key_app[] = "app";                  /* ROM 0x4d5f30 */
static const char key_enable[] = "enable";            /* ROM 0x78e65c */
static const char key_list[] = "list";                /* ROM 0x78e664 */
static const char key_id[] = "id";                    /* ROM 0x4d5f34 */
static const char key_name[] = "name";                /* ROM 0x78e66c */
static const char enabled[] = "ENABLED";              /* ROM 0x78e674 */
static const char disabled[] = "DISABLED";            /* ROM 0x78c0bc */

/* Plain record (level, line) plus the compressed record (mask) with the same args. */
#define WL_LOG(level, fn, line, mask, plain, compact, ...)                              \
    do {                                                                               \
        if ((audio_log_flags() & 2u) != 0u)                                            \
            audio_log_extended((level), module, path, (fn), (line), (plain), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)          \
            (void)compress_log_output((mask), (compact), (compact), ##__VA_ARGS__);    \
    } while (0)

/* 0x4d58d8: open flags to a stdio mode string. Only called with 1 ("r+").
 * The second branch is unreachable as written in the stock code: bit 1 is
 * part of the mask already tested. */
const char *whitelist_open_mode_4d58d8(uint32_t flags)
{
    if ((flags & 3u) != 0u) {
        if ((flags & 0x100u) != 0u)
            return (flags & 0x400u) != 0u ? "w+" : "a+"; /* ROM 0x4d5918 / 0x4d591c */
        return "r+";                                     /* ROM 0x4d5920 */
    }
    if ((flags & 2u) != 0u) {
        if ((flags & 0x800u) != 0u)
            return "a";                                  /* ROM 0x4d5924 */
        if ((flags & 0x100u) != 0u)
            return (flags & 0x400u) != 0u ? "w" : "a";   /* ROM 0x4d5928 / 0x4d5924 */
        return "w";
    }
    return "r";                                          /* ROM 0x4d592c */
}

/* File length via seek-to-end, restoring the current position; -1 on error. */
int32_t semantic_whitelist_file_size_preserving_position(void *file)
{
    int32_t position;
    int32_t size;

    if (file == NULL)
        return -1;
    position = file_tell(file);
    if (position < 0)
        return -1;
    if (file_seek(file, 0, 2) != 0) /* SEEK_END */
        return -1;
    size = file_tell(file);
    (void)file_seek(file, position, 0); /* SEEK_SET */
    return size;
}

static void set_flag(uint8_t mask, const g2_cjson_t *item)
{
    WL_INFO->flags = (uint8_t)((WL_INFO->flags & (uint8_t)~mask) |
                               (item->type == CJSON_TRUE ? mask : 0u));
}

static uint8_t missing_key(uint32_t line, g2_cjson_t *root, const char *key)
{
    static const char msg[] = "%s is NULL!\n";                    /* ROM 0x788fa0 */
    static const char msg_c[] = "[svc.whitelist]%s is NULL!\n";   /* ROM 0x771a2c */

    WL_LOG(1u, fn_parse_json, line, 0x04400000u, msg, msg_c, key);
    cJSON_Delete(root);
    return 0u;
}

/* Returns 1 when the top-level keys were found (also when "list" is not an
 * array), 0 on a parse error or a missing key. The count byte keeps the JSON
 * array size (clamped to 100) even when rows are skipped. */
uint8_t _parseJsonWhitelistToStruct(const char *json)
{
    static const char start[] = "[WHITELIST] Parsing JSON structure...";              /* ROM 0x74e68c */
    static const char start_c[] = "[svc.whitelist][WHITELIST] Parsing JSON structure..."; /* ROM 0x723268 */
    static const char bad_json[] = "Failed to parse JSON: %s";                        /* ROM 0x771a10 */
    static const char bad_json_c[] = "[svc.whitelist]Failed to parse JSON: %s";        /* ROM 0x74e6b4 */
    static const char no_app[] = "appJson is NULL!";                                  /* ROM 0x783730 */
    static const char no_app_c[] = "[svc.whitelist]appJson is NULL!";                 /* ROM 0x765490 */
    static const char no_list[] = "appListJson is NULL!";                             /* ROM 0x77bd34 */
    static const char no_list_c[] = "[svc.whitelist]appListJson is NULL!";            /* ROM 0x75a008 */
    static const char found[] = "[WHITELIST] Found %d apps in whitelist";             /* ROM 0x74e6dc */
    static const char found_c[] = "[svc.whitelist][WHITELIST] Found %d apps in whitelist"; /* ROM 0x7232a0 */
    static const char too_many[] = "[WHITELIST] App count (%d) exceeds limit (%d), truncating"; /* ROM 0x718a54 */
    static const char too_many_c[] =
        "[svc.whitelist][WHITELIST] App count (%d) exceeds limit (%d), truncating"; /* ROM 0x6f6108 */
    static const char bad_row[] = "Skipping invalid app at index %d";                  /* ROM 0x75a02c */
    static const char bad_row_c[] = "[svc.whitelist]Skipping invalid app at index %d"; /* ROM 0x738864 */
    static const char partial[] = "Skipping app with missing fields at index %d";      /* ROM 0x738894 */
    static const char partial_c[] =
        "[svc.whitelist]Skipping app with missing fields at index %d";                 /* ROM 0x718a90 */
    g2_app_whitelist_info_t *info = WL_INFO;
    g2_cjson_t *root;
    g2_cjson_t *item;
    g2_cjson_t *app;
    g2_cjson_t *list;

    WL_LOG(4u, fn_parse_json, 0x70u, 0x10000000u, start, start_c);
    root = cJSON_Parse(json);
    if (root == NULL) {
        WL_LOG(1u, fn_parse_json, 0x73u, 0x04400000u, bad_json, bad_json_c, json);
        return 0u;
    }
    audio_uart_buffer_zero(info, sizeof(*info), 0u);

    item = cJSON_GetObjectItem(root, key_call);
    if (item == NULL)
        return missing_key(0x7bu, root, key_call);
    set_flag(WL_FLAG_CALL, item);
    item = cJSON_GetObjectItem(root, key_msg);
    if (item == NULL)
        return missing_key(0x7cu, root, key_msg);
    set_flag(WL_FLAG_MSG, item);
    item = cJSON_GetObjectItem(root, key_calendar);
    if (item == NULL)
        return missing_key(0x7du, root, key_calendar);
    set_flag(WL_FLAG_CALENDAR, item);
    item = cJSON_GetObjectItem(root, key_mail);
    if (item == NULL)
        return missing_key(0x7eu, root, key_mail);
    set_flag(WL_FLAG_MAIL, item);

    app = cJSON_GetObjectItem(root, key_app);
    if (app == NULL) {
        WL_LOG(1u, fn_parse_json, 0x83u, 0x04000000u, no_app, no_app_c);
        cJSON_Delete(root);
        return 0u;
    }
    item = cJSON_GetObjectItem(app, key_enable);
    if (item == NULL)
        return missing_key(0x89u, root, key_enable);
    set_flag(WL_FLAG_APP, item);

    list = cJSON_GetObjectItem(app, key_list);
    if (list == NULL) {
        WL_LOG(1u, fn_parse_json, 0x8eu, 0x04000000u, no_list, no_list_c);
        cJSON_Delete(root);
        return 0u;
    }
    if (cJSON_IsArray(list) != 0) {
        uint8_t stored = 0u;

        info->count = (uint8_t)cJSON_GetArraySize(list);
        WL_LOG(3u, fn_parse_json, 0x95u, 0x0c400000u, found, found_c, info->count);
        if (info->count > WHITELIST_MAX_APPS) {
            WL_LOG(2u, fn_parse_json, 0x97u, 0x08800000u, too_many, too_many_c,
                   info->count, WHITELIST_MAX_APPS);
            info->count = WHITELIST_MAX_APPS;
        }
        for (uint8_t i = 0u; i < info->count; i++) {
            g2_cjson_t *row = cJSON_GetArrayItem(list, i);
            g2_cjson_t *id;
            g2_cjson_t *name;

            if (row == NULL) {
                WL_LOG(2u, fn_parse_json, 0x9fu, 0x08400000u, bad_row, bad_row_c, i);
                continue;
            }
            id = cJSON_GetObjectItem(row, key_id);
            name = cJSON_GetObjectItem(row, key_name);
            if (id == NULL || name == NULL) {
                WL_LOG(2u, fn_parse_json, 0xa7u, 0x08400000u, partial, partial_c, i);
                continue;
            }
            audio_uart_buffer_zero(info->apps[stored].id, sizeof(info->apps[stored].id), 0u);
            audio_uart_buffer_zero(info->apps[stored].name, sizeof(info->apps[stored].name), 0u);
            (void)audio_settings_copy_text(info->apps[stored].id, id->valuestring, 0x3fu);
            (void)audio_settings_copy_text(info->apps[stored].name, name->valuestring, 0xfu);
            stored++;
        }
    }
    cJSON_Delete(root);
    return 1u;
}

void _printAppWhiteListInfo(const g2_app_whitelist_info_t *info)
{
    static const char null_info[] = "[AppWhiteListInfo] NULL pointer!";                 /* ROM 0x75a050 */
    static const char null_info_c[] = "[svc.whitelist][AppWhiteListInfo] NULL pointer!"; /* ROM 0x7388c4 */
    static const char banner[] = "====== Whitelist Configuration ======";             /* ROM 0x74e704 */
    static const char banner_c[] = "[svc.whitelist]====== Whitelist Configuration ======"; /* ROM 0x7232d8 */
    static const char status[] = "[Status Flags]";                                     /* ROM 0x788fd0 */
    static const char status_c[] = "[svc.whitelist][Status Flags]";                    /* ROM 0x7654b0 */
    static const char call[] = "  Call Whitelist: %s";                                 /* ROM 0x77bd64 */
    static const char call_c[] = "[svc.whitelist]  Call Whitelist: %s";                /* ROM 0x75a074 */
    static const char sms[] = "  SMS Whitelist: %s";                                   /* ROM 0x783744 */
    static const char sms_c[] = "[svc.whitelist]  SMS Whitelist: %s";                  /* ROM 0x75a098 */
    static const char calendar[] = "  Calendar Whitelist: %s";                         /* ROM 0x771a48 */
    static const char calendar_c[] = "[svc.whitelist]  Calendar Whitelist: %s";        /* ROM 0x74e72c */
    static const char mail[] = "  Mail Whitelist: %s";                                 /* ROM 0x77bd7c */
    static const char mail_c[] = "[svc.whitelist]  Mail Whitelist: %s";                /* ROM 0x75a0bc */
    static const char apps[] = "  App Whitelist: %s";                                  /* ROM 0x783758 */
    static const char apps_c[] = "[svc.whitelist]  App Whitelist: %s";                 /* ROM 0x75a0e0 */
    static const char count[] = "[Application List] Count: %d";                        /* ROM 0x7654d0 */
    static const char count_c[] = "[svc.whitelist][Application List] Count: %d";       /* ROM 0x743b48 */
    static const char row[] = "  %02d. ID: %-24s Name: %s";                            /* ROM 0x771a64 */
    static const char row_c[] = "[svc.whitelist]  %02d. ID: %-24s Name: %s";           /* ROM 0x743b74 */
    static const char footer[] = "===================================";               /* ROM 0x75a104 */
    static const char footer_c[] = "[svc.whitelist]===================================";  /* ROM 0x72dba0 */

    if (info == NULL) {
        WL_LOG(4u, fn_print, 0xc0u, 0x10000000u, null_info, null_info_c);
        return;
    }
    WL_LOG(4u, fn_print, 0xc5u, 0x10000000u, banner, banner_c);
    WL_LOG(4u, fn_print, 0xc6u, 0x10000000u, status, status_c);
    WL_LOG(4u, fn_print, 0xc7u, 0x10400000u, call, call_c,
           (info->flags & WL_FLAG_CALL) != 0u ? enabled : disabled);
    WL_LOG(4u, fn_print, 0xc8u, 0x10400000u, sms, sms_c,
           (info->flags & WL_FLAG_MSG) != 0u ? enabled : disabled);
    WL_LOG(4u, fn_print, 0xc9u, 0x10400000u, calendar, calendar_c,
           (info->flags & WL_FLAG_CALENDAR) != 0u ? enabled : disabled);
    WL_LOG(4u, fn_print, 0xcau, 0x10400000u, mail, mail_c,
           (info->flags & WL_FLAG_MAIL) != 0u ? enabled : disabled);
    WL_LOG(4u, fn_print, 0xcbu, 0x10400000u, apps, apps_c,
           (info->flags & WL_FLAG_APP) != 0u ? enabled : disabled);
    WL_LOG(4u, fn_print, 0xceu, 0x10400000u, count, count_c, info->count);
    for (int32_t i = 0; i < (int32_t)info->count; i++)
        WL_LOG(4u, fn_print, 0xd0u, 0x10c00000u, row, row_c, i + 1,
               info->apps[i].id, info->apps[i].name);
    WL_LOG(4u, fn_print, 0xd2u, 0x10000000u, footer, footer_c);
}

/* Loads and parses the whitelist file. Small files are read into the shared
 * 0x20354c78 buffer, larger ones into a heap block of size + 1. Returns the
 * parse result; the CRC cache valid flag follows it. */
uint8_t _parseWhiteListFromFS(const char *file_path)
{
    static const char open_failed[] = "Failed to open file: %s";                     /* ROM 0x77bdac */
    static const char open_failed_c[] = "[svc.whitelist]Failed to open file: %s";    /* ROM 0x74e754 */
    static const char size_msg[] = "[WHITELIST] Whitelist file size: %ld bytes";     /* ROM 0x743ba0 */
    static const char size_msg_c[] =
        "[svc.whitelist][WHITELIST] Whitelist file size: %ld bytes";                  /* ROM 0x718acc */
    static const char bad_size[] = "[WHITELIST] Invalid file size: %ld";              /* ROM 0x75a128 */
    static const char bad_size_c[] = "[svc.whitelist][WHITELIST] Invalid file size: %ld"; /* ROM 0x72dbd4 */
    static const char shared[] = "use shared buffer, size is %ld";                    /* ROM 0x7654f0 */
    static const char shared_c[] = "[svc.whitelist]use shared buffer, size is %ld";   /* ROM 0x7388f4 */
    static const char heap[] = "use malloc buffer, size is %ld";                      /* ROM 0x765510 */
    static const char heap_c[] = "[svc.whitelist]use malloc buffer, size is %ld";     /* ROM 0x738924 */
    static const char no_mem[] = "malloc failed !";                                   /* ROM 0x788fe0 */
    static const char no_mem_c[] = "[svc.whitelist]malloc failed !";                  /* ROM 0x765530 */
    static const char short_read[] = "[WHITELIST] Read failed - expected %ld bytes, got %zu bytes"; /* ROM 0x718b08 */
    static const char short_read_c[] =
        "[svc.whitelist][WHITELIST] Read failed - expected %ld bytes, got %zu bytes"; /* ROM 0x6f6154 */
    static const char read_ok[] = "[WHITELIST] Successfully read %zu bytes from whitelist file"; /* ROM 0x718b44 */
    static const char read_ok_c[] =
        "[svc.whitelist][WHITELIST] Successfully read %zu bytes from whitelist file"; /* ROM 0x6f61a0 */
    static const char crc_msg[] = "[WHITELIST] CRC32 cache update: 0x%08x";          /* ROM 0x74e77c */
    static const char crc_msg_c[] = "[svc.whitelist][WHITELIST] CRC32 cache update: 0x%08x"; /* ROM 0x723310 */
    static const char loaded[] = "[WHITELIST] Whitelist loaded and parsed successfully"; /* ROM 0x723348 */
    static const char loaded_c[] =
        "[svc.whitelist][WHITELIST] Whitelist loaded and parsed successfully";        /* ROM 0x705e64 */
    static const char parse_failed[] = "[WHITELIST] Failed to parse whitelist JSON"; /* ROM 0x743bcc */
    static const char parse_failed_c[] =
        "[svc.whitelist][WHITELIST] Failed to parse whitelist JSON";                  /* ROM 0x718b80 */
    void *file;
    int32_t size;
    uint8_t *buffer;
    uint32_t got;
    uint8_t result;

    file = file_open(file_path, whitelist_open_mode_4d58d8(1u));
    if (file == NULL) {
        WL_LOG(1u, fn_parse_fs, 0xdbu, 0x04400000u, open_failed, open_failed_c, file_path);
        audio_message_notify_crc_valid_2007501b = 0u;
        return 0u;
    }
    size = semantic_whitelist_file_size_preserving_position(file);
    WL_LOG(4u, fn_parse_fs, 0xe2u, 0x10400000u, size_msg, size_msg_c, size);
    if (size < 1) {
        WL_LOG(1u, fn_parse_fs, 0xe4u, 0x04400000u, bad_size, bad_size_c, size);
        (void)file_close(file);
        audio_message_notify_crc_valid_2007501b = 0u;
        return 0u;
    }
    if ((uint32_t)size < WHITELIST_SHARED_BUFFER_LIMIT) {
        buffer = svc_android_notify_buffer_48e0a8();
        WL_LOG(4u, fn_parse_fs, 0xedu, 0x10400000u, shared, shared_c, size);
    } else {
        buffer = file_heap_allocate((uint32_t)size + 1u);
        WL_LOG(4u, fn_parse_fs, 0xf0u, 0x10400000u, heap, heap_c, size);
    }
    if (buffer == NULL) {
        WL_LOG(1u, fn_parse_fs, 0xf3u, 0x04000000u, no_mem, no_mem_c);
        (void)file_close(file);
        audio_message_notify_crc_valid_2007501b = 0u;
        return 0u;
    }

    got = file_read(buffer, 1u, (uint32_t)size, file);
    (void)file_close(file);
    if (got != (uint32_t)size) {
        WL_LOG(1u, fn_parse_fs, 0xfeu, 0x04800000u, short_read, short_read_c, size, got);
        if (buffer != svc_android_notify_buffer_48e0a8())
            file_heap_free(buffer);
        audio_message_notify_crc_valid_2007501b = 0u;
        return 0u;
    }
    WL_LOG(4u, fn_parse_fs, 0x105u, 0x10400000u, read_ok, read_ok_c, got);
    buffer[size] = 0u;
    result = _parseJsonWhitelistToStruct((const char *)buffer);
    if (result == 0u) {
        audio_message_notify_crc_valid_2007501b = 0u;
        WL_LOG(1u, fn_parse_fs, 0x114u, 0x04000000u, parse_failed, parse_failed_c);
    } else {
        uint32_t crc = 0u;

        file_crc32c_update_47cbc4(buffer, (uint32_t)size, &crc);
        audio_message_notify_cached_crc_200749a4 = crc;
        audio_message_notify_crc_valid_2007501b = 1u;
        WL_LOG(3u, fn_parse_fs, 0x110u, 0x0c400000u, crc_msg, crc_msg_c,
               audio_message_notify_cached_crc_200749a4);
        WL_LOG(4u, fn_parse_fs, 0x111u, 0x10000000u, loaded, loaded_c);
    }
    if (buffer != svc_android_notify_buffer_48e0a8())
        file_heap_free(buffer);
    return result;
}

void SVC_WhitelistManagerInit(void)
{
    static const char buf_len[] = "MAX_WHITE_LIST_BUF_LEN is %d ";                /* ROM 0x765590 */
    static const char buf_len_c[] = "[svc.whitelist]MAX_WHITE_LIST_BUF_LEN is %d "; /* ROM 0x738984 */
    g2_app_whitelist_info_t *info = WL_INFO;

    audio_uart_buffer_zero(info, sizeof(*info), 0u);
    WL_LOG(4u, fn_init, 0x1b7u, 0x10400000u, buf_len, buf_len_c, 0x1f43u);
    (void)_parseWhiteListFromFS(whitelist_path);
    _printAppWhiteListInfo(info);
}
