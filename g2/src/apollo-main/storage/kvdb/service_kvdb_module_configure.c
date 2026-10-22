/* Module configuration KV records (language, dashboard auto-close, menu), stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_module_configure.c.
 * Native 0x4922f8..0x492be5; literal pool 0x492be8..0x492cb3.
 *
 * The three readers are registered migration callbacks. Their stock __func__
 * strings are _kvdbUpdataLanguage, _kvdbUpdataDashboardAutoCloseValue and
 * _kvdbUpdataMenuConfigureValue; the TSV anchor names are kept.
 *
 *   kvSystemLanguage           1 byte, valid 0..7, default 0 -> RAM 0x20000030 (word)
 *   kvDashboardAutoCloseValue  4 bytes, default 10        -> RAM 0x20000038 (word)
 *   kvMenuConfigureValue       0x378 bytes (magic 0x5555aaaa, count, 20 x 44-byte items)
 *                              mirrored into the menu page item table at RAM 0x2006ad0c */
#include "kvdb_private.h"

typedef struct {
    const void *icon;      /* +0x00 lv_image_dsc_t */
    char text[32];         /* +0x04 */
    uint32_t text_res;     /* +0x24 0xffe for custom apps */
    uint8_t app_type;      /* +0x28 */
    uint8_t reserved[3];
    int32_t icon_num;      /* +0x2c */
    int32_t app_id;        /* +0x30 */
} g2_menu_page_item_t;
_Static_assert(sizeof(g2_menu_page_item_t) == 0x34, "menu page item");

#define LANGUAGE_COUNT 8u
#define DASHBOARD_AUTO_CLOSE_DEFAULT 10u
#define SERVICE_MODE_FACTORY 2u
#define CUSTOM_TEXT_RES 0xffeu
#define CUSTOM_APP_TYPE 1u

extern volatile uint32_t audio_uart_display_locale_index;   /* RAM 0x20000030, default 0 */
extern uint32_t g2_kvdb_dashboard_auto_close_value;         /* RAM 0x20000038, default 10 */
extern g2_menu_page_item_t g2_menu_page_items[G2_KVDB_MENU_ITEM_MAX]; /* RAM 0x2006ad0c */
extern int32_t g2_menu_use_ext_items;                       /* RAM 0x200746fc */
extern int32_t g2_menu_ext_item_count;                      /* RAM 0x20074700 */
extern const uint8_t g2_menu_custom_app_icon[];             /* ROM 0x76b7bc, 24x24 lv_image_dsc_t */

g2_kvdb_menu_configure_t g2_kvdb_menu_configure_record;     /* RAM 0x2006d43c */

extern uint32_t audio_uart_service_mode(void);                          /* 0x45a570 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);         /* memset(p, n, c) 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);    /* memcpy 0x439be4 */
extern uint32_t g2_log_module_length(const char *);                     /* strlen 0x44a43c */
extern int32_t audio_uart_font_path_compare(const char *, const char *); /* strcmp 0x46cacc */
extern uint32_t audio_uart_page_460084(const char *);                   /* i18n index of text */
extern uint32_t audio_uart_page_45fffe(const char *, uint32_t);         /* localized text */
extern int32_t menu_builtin_app_info_get_460450(int32_t app_id, const void **icon, char *text,
                                                uint32_t *text_res, uint8_t *app_type);
extern void menu_page_mutex_lock_46018e(void);
extern void menu_page_mutex_unlock_4601ea(void);

static const char module_tag[] = "kv.module_cfg"; /* ROM 0x788aa0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv\\service_kvdb_module_configure.c"; /* ROM 0x6de674 */

static const char key_language[] = "kvSystemLanguage"; /* ROM 0x783348 */
static const char language_fn[] = "_kvdbUpdataLanguage"; /* ROM 0x783334 */
static const char language_msg[] = "SVC_KvdbReadLanguage: language_index = %d"; /* ROM 0x7432dc */
static const char language_msg_short[] = "[kv.module_cfg]SVC_KvdbReadLanguage: language_index = %d"; /* ROM 0x71861c */
static const char language_default_msg[] =
    " KV get value failed.SVC_KvdbReadLanguage set default value: language_index = %d"; /* ROM 0x6e9c94 */
static const char language_default_msg_short[] =
    "[kv.module_cfg] KV get value failed.SVC_KvdbReadLanguage set default value: language_index = %d"; /* ROM 0x6de6d4 */

static const char key_dashboard[] = "kvDashboardAutoCloseValue"; /* ROM 0x77132c */
static const char dashboard_fn[] = "_kvdbUpdataDashboardAutoCloseValue"; /* ROM 0x759b1c */
static const char dashboard_msg[] =
    "SVC_KvdbReadDashboardAutoCloseValue: dashboard_auto_close_value = %d"; /* ROM 0x6fce3c */
static const char dashboard_msg_short[] =
    "[kv.module_cfg]SVC_KvdbReadDashboardAutoCloseValue: dashboard_auto_close_value = %d"; /* ROM 0x6e9ce8 */
static const char dashboard_default_msg[] =
    "kv get value failed. SVC_KvdbReadDashboardAutoCloseValue set default value: dashboard_auto_close_value = %d"; /* ROM 0x6d7da4 */
static const char dashboard_default_msg_short[] =
    "[kv.module_cfg]kv get value failed. SVC_KvdbReadDashboardAutoCloseValue set default value: dashboard_auto_close_value = %d"; /* ROM 0x69c614 */

static const char key_menu[] = "kvMenuConfigureValue"; /* ROM 0x77b944 */
static const char menu_read_fn[] = "_kvdbUpdataMenuConfigureValue"; /* ROM 0x764fd0 */
static const char menu_default_msg[] =
    "kv get value failed. SVC_KvdbReadMenuConfigureValue set default value"; /* ROM 0x6fcfa4 */
static const char menu_default_msg_short[] =
    "[kv.module_cfg]kv get value failed. SVC_KvdbReadMenuConfigureValue set default value"; /* ROM 0x6e4ed8 */
static const char menu_total_msg[] =
    "SVC_KvdbReadMenuConfigureValue: menu_configure_total_count = %d"; /* ROM 0x70eda4 */
static const char menu_total_msg_short[] =
    "[kv.module_cfg]SVC_KvdbReadMenuConfigureValue: menu_configure_total_count = %d"; /* ROM 0x6efa48 */
static const char menu_type_msg[] =
    "SVC_KvdbReadMenuConfigureValue: menu_configure_item[%d].app_type = %d"; /* ROM 0x6fce84 */
static const char menu_type_msg_short[] =
    "[kv.module_cfg]SVC_KvdbReadMenuConfigureValue: menu_configure_item[%d].app_type = %d"; /* ROM 0x6e4d78 */
static const char menu_icon_msg[] =
    "SVC_KvdbReadMenuConfigureValue: menu_configure_item[%d].icon_num = %d"; /* ROM 0x6fcecc */
static const char menu_icon_msg_short[] =
    "[kv.module_cfg]SVC_KvdbReadMenuConfigureValue: menu_configure_item[%d].icon_num = %d"; /* ROM 0x6e4dd0 */
static const char menu_text_msg[] =
    "SVC_KvdbReadMenuConfigureValue: menu_configure_item[%d].text_name = %s"; /* ROM 0x6fcf14 */
static const char menu_text_msg_short[] =
    "[kv.module_cfg]SVC_KvdbReadMenuConfigureValue: menu_configure_item[%d].text_name = %s"; /* ROM 0x6e4e28 */
static const char menu_id_msg[] =
    "SVC_KvdbReadMenuConfigureValue: menu_configure_item[%d].app_id = %d"; /* ROM 0x7059e0 */
static const char menu_id_msg_short[] =
    "[kv.module_cfg]SVC_KvdbReadMenuConfigureValue: menu_configure_item[%d].app_id = %d"; /* ROM 0x6e9d3c */
static const char menu_builtin_msg[] =
    "menu page recv data from BLE, get builtin app info failed, app_id = %d"; /* ROM 0x6fcf5c */
static const char menu_builtin_msg_short[] =
    "[kv.module_cfg]menu page recv data from BLE, get builtin app info failed, app_id = %d"; /* ROM 0x6e4e80 */
static const char menu_custom_msg[] = "text = %s,app_id = %d,app_type = %d"; /* ROM 0x759b40 */
static const char menu_custom_msg_short[] = "[kv.module_cfg]text = %s,app_id = %d,app_type = %d"; /* ROM 0x72d5f0 */

static const char menu_write_fn[] = "SVC_KvdbWriteMenuConfigureValue"; /* ROM 0x764ff0 */
static const char menu_ext_msg[] = "use_ext_menu_items = %d, ext_menu_items_count = %d"; /* ROM 0x72d658 */
static const char menu_ext_msg_short[] =
    "[kv.module_cfg]use_ext_menu_items = %d, ext_menu_items_count = %d"; /* ROM 0x705a24 */
static const char menu_stored_msg[] = "Read menu configure from KV, total_count = %d"; /* ROM 0x738504 */
static const char menu_stored_msg_short[] =
    "[kv.module_cfg]Read menu configure from KV, total_count = %d"; /* ROM 0x70ede4 */
static const char menu_diff_msg[] = "Menu configure item[%d] is different"; /* ROM 0x74df34 */
static const char menu_diff_msg_short[] = "[kv.module_cfg]Menu configure item[%d] is different"; /* ROM 0x72d624 */
static const char menu_same_msg[] = "Menu configure is same as KV, skip write"; /* ROM 0x743308 */
static const char menu_same_msg_short[] = "[kv.module_cfg]Menu configure is same as KV, skip write"; /* ROM 0x722cf0 */
static const char menu_save_msg[] = "MenuConfigureValueSaveToFlash, write to KV"; /* ROM 0x743334 */
static const char menu_save_msg_short[] = "[kv.module_cfg]MenuConfigureValueSaveToFlash, write to KV"; /* ROM 0x718658 */

int32_t SVC_KvdbReadLanguage(void) {
    uint8_t language;
    if (SVC_KvdbBlobRead(key_language, &language, 1u) > 0) {
        G2_KV_LOG(3u, module_tag, source_file, language_fn, 29u, language_msg, language_msg_short,
                  0x0c400000u, language);
        if (language < LANGUAGE_COUNT) {
            G2_KV_LOG(3u, module_tag, source_file, language_fn, 31u, language_msg,
                      language_msg_short, 0x0c400000u, language);
            audio_uart_display_locale_index = language;
            return 0;
        }
    }
    audio_uart_display_locale_index = 0u;
    G2_KV_LOG(3u, module_tag, source_file, language_fn, 37u, language_default_msg,
              language_default_msg_short, 0x0c400000u, audio_uart_display_locale_index);
    return 0;
}
G2_KVDB_MIGRATION_EXPORT(SVC_KvdbReadLanguage);

int32_t SVC_KvdbWriteLanguage(uint8_t language) {
    return audio_settings_kvdb_blob_write(key_language, &language, 1u);
}

/* Skipped in service mode 2. */
int32_t SVC_KvdbReadDashboardAutoCloseValue(void) {
    uint32_t value;
    if (audio_uart_service_mode() == SERVICE_MODE_FACTORY)
        return 0;
    audio_uart_buffer_zero(&value, sizeof(value), 0u);
    if (SVC_KvdbBlobRead(key_dashboard, &value, 4u) > 0) {
        g2_kvdb_dashboard_auto_close_value = value;
        G2_KV_LOG(3u, module_tag, source_file, dashboard_fn, 72u, dashboard_msg, dashboard_msg_short,
                  0x0c400000u, g2_kvdb_dashboard_auto_close_value);
        return 0;
    }
    g2_kvdb_dashboard_auto_close_value = DASHBOARD_AUTO_CLOSE_DEFAULT;
    G2_KV_LOG(3u, module_tag, source_file, dashboard_fn, 76u, dashboard_default_msg,
              dashboard_default_msg_short, 0x0c400000u, g2_kvdb_dashboard_auto_close_value);
    return 0;
}
G2_KVDB_MIGRATION_EXPORT(SVC_KvdbReadDashboardAutoCloseValue);

int32_t SVC_KvdbWriteDashboardAutoCloseValue(uint32_t value) {
    return audio_settings_kvdb_blob_write(key_dashboard, &value, 4u);
}

/* Rebuild the menu page from the stored layout: built-in apps (type 0) take
 * icon and text from the built-in table, others get the custom icon. Copied
 * text is not NUL-terminated beyond the zeroed destination. */
int32_t SVC_KvdbReadMenuConfigureValue(void) {
    g2_kvdb_menu_configure_t *record = &g2_kvdb_menu_configure_record;
    audio_uart_buffer_zero(record, sizeof(*record), 0u);
    if (SVC_KvdbBlobRead(key_menu, record, (uint16_t)sizeof(*record)) < 1 ||
        record->magic != G2_KVDB_MENU_MAGIC) {
        G2_KV_LOG(4u, module_tag, source_file, menu_read_fn, 141u, menu_default_msg,
                  menu_default_msg_short, 0x10000000u);
        return 0;
    }
    G2_KV_LOG(3u, module_tag, source_file, menu_read_fn, 114u, menu_total_msg, menu_total_msg_short,
              0x0c400000u, record->total_count);
    for (int32_t i = 0; i < (int32_t)record->total_count; i++) {
        const g2_kvdb_menu_item_t *item = &record->items[i];
        g2_menu_page_item_t *page = &g2_menu_page_items[i];
        G2_KV_LOG(3u, module_tag, source_file, menu_read_fn, 116u, menu_type_msg,
                  menu_type_msg_short, 0x0c800000u, i, item->app_type);
        G2_KV_LOG(3u, module_tag, source_file, menu_read_fn, 117u, menu_icon_msg,
                  menu_icon_msg_short, 0x0c800000u, i, item->icon_num);
        G2_KV_LOG(3u, module_tag, source_file, menu_read_fn, 118u, menu_text_msg,
                  menu_text_msg_short, 0x0c800000u, i, item->text_name);
        G2_KV_LOG(3u, module_tag, source_file, menu_read_fn, 119u, menu_id_msg, menu_id_msg_short,
                  0x0c800000u, i, item->app_id);
        if (item->app_type == 0u) {
            if (menu_builtin_app_info_get_460450(item->app_id, &page->icon, page->text,
                                                 &page->text_res, &page->app_type) != 0) {
                G2_KV_LOG(1u, module_tag, source_file, menu_read_fn, 124u, menu_builtin_msg,
                          menu_builtin_msg_short, 0x04400000u, item->app_id);
                return -1;
            }
            page->app_id = item->app_id;
        } else {
            page->app_id = item->app_id;
            page->text_res = CUSTOM_TEXT_RES;
            page->app_type = CUSTOM_APP_TYPE;
            page->icon = g2_menu_custom_app_icon;
            audio_queue_copy_bytes(page->text, item->text_name, g2_log_module_length(item->text_name));
            G2_KV_LOG(3u, module_tag, source_file, menu_read_fn, 134u, menu_custom_msg,
                      menu_custom_msg_short, 0x0cc00000u,
                      audio_uart_page_45fffe(page->text, audio_uart_page_460084(page->text)),
                      page->app_id, page->app_type);
        }
    }
    g2_menu_use_ext_items = 1;
    g2_menu_ext_item_count = (int32_t)record->total_count;
    return 0;
}
G2_KVDB_MIGRATION_EXPORT(SVC_KvdbReadMenuConfigureValue);

/* Persist the menu page layout unless the stored copy already matches it. */
int32_t SVC_KvdbWriteMenuConfigureValue(void) {
    g2_kvdb_menu_configure_t *record = &g2_kvdb_menu_configure_record;
    if (g2_menu_use_ext_items != 1 || g2_menu_ext_item_count < 1) {
        G2_KV_LOG(2u, module_tag, source_file, menu_write_fn, 196u, menu_ext_msg, menu_ext_msg_short,
                  0x08800000u, g2_menu_use_ext_items, g2_menu_ext_item_count);
        return -1;
    }
    audio_uart_buffer_zero(record, sizeof(*record), 0u);
    if (SVC_KvdbBlobRead(key_menu, record, (uint16_t)sizeof(*record)) > 0 &&
        record->magic == G2_KVDB_MENU_MAGIC) {
        G2_KV_LOG(4u, module_tag, source_file, menu_write_fn, 157u, menu_stored_msg,
                  menu_stored_msg_short, 0x10400000u, record->total_count);
        if ((int32_t)record->total_count == g2_menu_ext_item_count) {
            bool same = true;
            for (int32_t i = 0; i < g2_menu_ext_item_count; i++) {
                const g2_kvdb_menu_item_t *item = &record->items[i];
                const g2_menu_page_item_t *page = &g2_menu_page_items[i];
                if (item->app_type != page->app_type || item->app_id != page->app_id ||
                    item->icon_num != page->icon_num ||
                    audio_uart_font_path_compare(item->text_name, page->text) != 0) {
                    same = false;
                    G2_KV_LOG(4u, module_tag, source_file, menu_write_fn, 170u, menu_diff_msg,
                              menu_diff_msg_short, 0x10400000u, i);
                    break;
                }
            }
            if (same) {
                G2_KV_LOG(3u, module_tag, source_file, menu_write_fn, 177u, menu_same_msg,
                          menu_same_msg_short, 0x0c000000u);
                return 0;
            }
        }
    }
    audio_uart_buffer_zero(record, sizeof(*record), 0u);
    menu_page_mutex_lock_46018e();
    record->magic = G2_KVDB_MENU_MAGIC;
    record->total_count = (uint8_t)g2_menu_ext_item_count;
    for (int32_t i = 0; i < g2_menu_ext_item_count; i++) {
        g2_kvdb_menu_item_t *item = &record->items[i];
        const g2_menu_page_item_t *page = &g2_menu_page_items[i];
        item->app_type = page->app_type;
        item->icon_num = page->icon_num;
        audio_queue_copy_bytes(item->text_name, page->text, g2_log_module_length(page->text));
        item->app_id = page->app_id;
    }
    menu_page_mutex_unlock_4601ea();
    G2_KV_LOG(3u, module_tag, source_file, menu_write_fn, 199u, menu_save_msg, menu_save_msg_short,
              0x0c000000u);
    return audio_settings_kvdb_blob_write(key_menu, record, sizeof(*record));
}
