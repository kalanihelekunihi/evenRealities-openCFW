/* Clean-room reconstruction of service_kvdb_module_configure.c. */

#include <stddef.h>
#include <stdint.h>

enum {
    OPEN_CFW_KVDB_MODULE_MENU_CAPACITY = 20,
    OPEN_CFW_KVDB_MODULE_MENU_TEXT_BYTES = 32,
};

typedef struct {
    uint8_t icon_num;
    uint8_t padding[3];
    uint32_t app_type;
    char text_name[OPEN_CFW_KVDB_MODULE_MENU_TEXT_BYTES];
    uint32_t app_id;
} open_cfw_kvdb_module_menu_record_item;

typedef struct {
    uint32_t magic;
    uint8_t count;
    uint8_t padding[3];
    open_cfw_kvdb_module_menu_record_item
        items[OPEN_CFW_KVDB_MODULE_MENU_CAPACITY];
} open_cfw_kvdb_module_menu_record;

typedef struct {
    uint32_t resource;
    char text[OPEN_CFW_KVDB_MODULE_MENU_TEXT_BYTES];
    uint32_t page_value;
    uint8_t icon_num;
    uint8_t padding[3];
    uint32_t app_type;
    uint32_t app_id;
} open_cfw_kvdb_module_runtime_menu_item;

_Static_assert(sizeof(open_cfw_kvdb_module_menu_record_item) == 44,
    "stock stored menu item must remain forty-four bytes");
_Static_assert(offsetof(open_cfw_kvdb_module_menu_record_item, app_type) == 4,
    "stored app type must remain at offset four");
_Static_assert(offsetof(open_cfw_kvdb_module_menu_record_item, text_name) == 8,
    "stored menu text must remain at offset eight");
_Static_assert(offsetof(open_cfw_kvdb_module_menu_record_item, app_id) == 40,
    "stored app ID must remain at offset forty");
_Static_assert(sizeof(open_cfw_kvdb_module_menu_record) == 888,
    "stock menu record must remain 888 bytes");
_Static_assert(sizeof(open_cfw_kvdb_module_runtime_menu_item) == 52,
    "stock runtime menu item must remain fifty-two bytes");
_Static_assert(offsetof(open_cfw_kvdb_module_runtime_menu_item, text) == 4,
    "runtime text must remain at offset four");
_Static_assert(offsetof(open_cfw_kvdb_module_runtime_menu_item, page_value) == 36,
    "runtime page value must remain at offset thirty-six");
_Static_assert(offsetof(open_cfw_kvdb_module_runtime_menu_item, icon_num) == 40,
    "runtime icon number must remain at offset forty");
_Static_assert(offsetof(open_cfw_kvdb_module_runtime_menu_item, app_type) == 44,
    "runtime app type must remain at offset forty-four");
_Static_assert(offsetof(open_cfw_kvdb_module_runtime_menu_item, app_id) == 48,
    "runtime app ID must remain at offset forty-eight");

#ifndef OPEN_CFW_KVDB_MODULE_LANGUAGE_ADDRESS
#define OPEN_CFW_KVDB_MODULE_LANGUAGE_ADDRESS 0x20000030u
#endif
#ifndef OPEN_CFW_KVDB_MODULE_DASHBOARD_ADDRESS
#define OPEN_CFW_KVDB_MODULE_DASHBOARD_ADDRESS 0x20000038u
#endif
#ifndef OPEN_CFW_KVDB_MODULE_MENU_RECORD_ADDRESS
#define OPEN_CFW_KVDB_MODULE_MENU_RECORD_ADDRESS 0x2006d43cu
#endif
#ifndef OPEN_CFW_KVDB_MODULE_RUNTIME_MENU_ADDRESS
#define OPEN_CFW_KVDB_MODULE_RUNTIME_MENU_ADDRESS 0x2006ad0cu
#endif
#ifndef OPEN_CFW_KVDB_MODULE_USE_EXTERNAL_ADDRESS
#define OPEN_CFW_KVDB_MODULE_USE_EXTERNAL_ADDRESS 0x200746fcu
#endif
#ifndef OPEN_CFW_KVDB_MODULE_EXTERNAL_COUNT_ADDRESS
#define OPEN_CFW_KVDB_MODULE_EXTERNAL_COUNT_ADDRESS 0x20074700u
#endif
#ifndef OPEN_CFW_KVDB_MODULE_CUSTOM_RESOURCE_ADDRESS
#define OPEN_CFW_KVDB_MODULE_CUSTOM_RESOURCE_ADDRESS 0x0076b7bcu
#endif

#ifndef OPEN_CFW_KVDB_MODULE_READ
int open_cfw_kvdb_module_db_read(
    const char *key, void *value, uint16_t length
);
#define OPEN_CFW_KVDB_MODULE_READ(key, value, length) \
    open_cfw_kvdb_module_db_read((key), (value), (length))
#endif
#ifndef OPEN_CFW_KVDB_MODULE_WRITE
int open_cfw_kvdb_module_db_write(
    const char *key, const void *value, uint16_t length
);
#define OPEN_CFW_KVDB_MODULE_WRITE(key, value, length) \
    open_cfw_kvdb_module_db_write((key), (value), (length))
#endif
#ifndef OPEN_CFW_KVDB_MODULE_DASHBOARD_MODE
int open_cfw_kvdb_module_dashboard_mode(void);
#define OPEN_CFW_KVDB_MODULE_DASHBOARD_MODE() \
    open_cfw_kvdb_module_dashboard_mode()
#endif
#ifndef OPEN_CFW_KVDB_MODULE_LOOKUP_BUILTIN
int open_cfw_kvdb_module_lookup_builtin(
    uint32_t app_id,
    open_cfw_kvdb_module_runtime_menu_item *item,
    char *text,
    uint32_t *page_value,
    uint8_t *icon_num
);
#define OPEN_CFW_KVDB_MODULE_LOOKUP_BUILTIN(app_id, item, text, page, icon) \
    open_cfw_kvdb_module_lookup_builtin( \
        (app_id), (item), (text), (page), (icon) \
    )
#endif
#ifndef OPEN_CFW_KVDB_MODULE_SNAPSHOT_BEGIN
void open_cfw_kvdb_module_snapshot_begin(void);
#define OPEN_CFW_KVDB_MODULE_SNAPSHOT_BEGIN() \
    open_cfw_kvdb_module_snapshot_begin()
#endif
#ifndef OPEN_CFW_KVDB_MODULE_SNAPSHOT_END
void open_cfw_kvdb_module_snapshot_end(void);
#define OPEN_CFW_KVDB_MODULE_SNAPSHOT_END() \
    open_cfw_kvdb_module_snapshot_end()
#endif
#ifndef OPEN_CFW_KVDB_MODULE_DIAGNOSTIC
#define OPEN_CFW_KVDB_MODULE_DIAGNOSTIC() ((void)0)
#endif

#define OPEN_CFW_KVDB_MODULE_LANGUAGE \
    (*(volatile uint32_t *)(uintptr_t)OPEN_CFW_KVDB_MODULE_LANGUAGE_ADDRESS)
#define OPEN_CFW_KVDB_MODULE_DASHBOARD \
    (*(volatile uint32_t *)(uintptr_t)OPEN_CFW_KVDB_MODULE_DASHBOARD_ADDRESS)
#define OPEN_CFW_KVDB_MODULE_MENU_RECORD \
    ((open_cfw_kvdb_module_menu_record *)(uintptr_t) \
        OPEN_CFW_KVDB_MODULE_MENU_RECORD_ADDRESS)
#define OPEN_CFW_KVDB_MODULE_RUNTIME_MENU \
    ((open_cfw_kvdb_module_runtime_menu_item *)(uintptr_t) \
        OPEN_CFW_KVDB_MODULE_RUNTIME_MENU_ADDRESS)
#define OPEN_CFW_KVDB_MODULE_USE_EXTERNAL \
    (*(volatile uint32_t *)(uintptr_t) \
        OPEN_CFW_KVDB_MODULE_USE_EXTERNAL_ADDRESS)
#define OPEN_CFW_KVDB_MODULE_EXTERNAL_COUNT \
    (*(volatile uint32_t *)(uintptr_t) \
        OPEN_CFW_KVDB_MODULE_EXTERNAL_COUNT_ADDRESS)
#define OPEN_CFW_KVDB_MODULE_CUSTOM_RESOURCE \
    ((uint32_t)OPEN_CFW_KVDB_MODULE_CUSTOM_RESOURCE_ADDRESS)

#define OPEN_CFW_KVDB_MODULE_LANGUAGE_KEY "kvSystemLanguage"
#define OPEN_CFW_KVDB_MODULE_DASHBOARD_KEY "kvDashboardAutoCloseValue"
#define OPEN_CFW_KVDB_MODULE_MENU_KEY "kvMenuConfigureValue"
#define OPEN_CFW_KVDB_MODULE_MENU_MAGIC 0x5555aaaau

static void open_cfw_kvdb_module_zero(void *destination, uint32_t length)
{
    uint8_t *bytes = destination;
    while (length-- != 0u) {
        *bytes++ = 0u;
    }
}

static uint32_t open_cfw_kvdb_module_string_length(const char *text)
{
    uint32_t length = 0u;
    while (text[length] != '\0') {
        ++length;
    }
    return length;
}

static void open_cfw_kvdb_module_copy(
    void *destination, const void *source, uint32_t length
)
{
    uint8_t *out = destination;
    const uint8_t *in = source;
    while (length-- != 0u) {
        *out++ = *in++;
    }
}

static int open_cfw_kvdb_module_string_compare(
    const char *left, const char *right
)
{
    while (*left == *right && *left != '\0') {
        ++left;
        ++right;
    }
    return (int)(uint8_t)*left - (int)(uint8_t)*right;
}

int open_cfw_kvdb_read_language(void)
{
    uint8_t stored = 0u;

    if (OPEN_CFW_KVDB_MODULE_READ(
            OPEN_CFW_KVDB_MODULE_LANGUAGE_KEY, &stored, 1u
        ) >= 1 && stored < 8u) {
        OPEN_CFW_KVDB_MODULE_DIAGNOSTIC();
        OPEN_CFW_KVDB_MODULE_LANGUAGE = stored;
        return 0;
    }
    OPEN_CFW_KVDB_MODULE_LANGUAGE = 0u;
    OPEN_CFW_KVDB_MODULE_DIAGNOSTIC();
    return 0;
}

void open_cfw_kvdb_write_language(uint8_t language)
{
    (void)OPEN_CFW_KVDB_MODULE_WRITE(
        OPEN_CFW_KVDB_MODULE_LANGUAGE_KEY, &language, 1u
    );
}

int open_cfw_kvdb_read_dashboard_auto_close(void)
{
    uint32_t stored = 0u;

    if (OPEN_CFW_KVDB_MODULE_DASHBOARD_MODE() == 2) {
        return 0;
    }
    if (OPEN_CFW_KVDB_MODULE_READ(
            OPEN_CFW_KVDB_MODULE_DASHBOARD_KEY, &stored, sizeof(stored)
        ) >= 1) {
        OPEN_CFW_KVDB_MODULE_DASHBOARD = stored;
    } else {
        OPEN_CFW_KVDB_MODULE_DASHBOARD = 10u;
    }
    OPEN_CFW_KVDB_MODULE_DIAGNOSTIC();
    return 0;
}

void open_cfw_kvdb_write_dashboard_auto_close(uint32_t value)
{
    (void)OPEN_CFW_KVDB_MODULE_WRITE(
        OPEN_CFW_KVDB_MODULE_DASHBOARD_KEY, &value, sizeof(value)
    );
}

int open_cfw_kvdb_read_menu_configuration(void)
{
    open_cfw_kvdb_module_menu_record *record =
        OPEN_CFW_KVDB_MODULE_MENU_RECORD;
    open_cfw_kvdb_module_runtime_menu_item *runtime =
        OPEN_CFW_KVDB_MODULE_RUNTIME_MENU;
    uint32_t index;

    open_cfw_kvdb_module_zero(record, sizeof(*record));
    if (OPEN_CFW_KVDB_MODULE_READ(
            OPEN_CFW_KVDB_MODULE_MENU_KEY, record, sizeof(*record)
        ) < 1 || record->magic != OPEN_CFW_KVDB_MODULE_MENU_MAGIC) {
        OPEN_CFW_KVDB_MODULE_DIAGNOSTIC();
        return 0;
    }

    OPEN_CFW_KVDB_MODULE_DIAGNOSTIC();
    for (index = 0; index < record->count; ++index) {
        open_cfw_kvdb_module_menu_record_item *stored = &record->items[index];
        open_cfw_kvdb_module_runtime_menu_item *live = &runtime[index];

        OPEN_CFW_KVDB_MODULE_DIAGNOSTIC();
        if (stored->icon_num == 0u) {
            if (OPEN_CFW_KVDB_MODULE_LOOKUP_BUILTIN(
                    stored->app_id, live, live->text,
                    &live->page_value, &live->icon_num
                ) != 0) {
                OPEN_CFW_KVDB_MODULE_DIAGNOSTIC();
                return -1;
            }
            live->app_id = stored->app_id;
        } else {
            uint32_t length;
            live->app_id = stored->app_id;
            live->page_value = 0xffeu;
            live->icon_num = 1u;
            live->resource = OPEN_CFW_KVDB_MODULE_CUSTOM_RESOURCE;
            length = open_cfw_kvdb_module_string_length(stored->text_name);
            open_cfw_kvdb_module_copy(live->text, stored->text_name, length);
            OPEN_CFW_KVDB_MODULE_DIAGNOSTIC();
        }
    }
    OPEN_CFW_KVDB_MODULE_USE_EXTERNAL = 1u;
    OPEN_CFW_KVDB_MODULE_EXTERNAL_COUNT = record->count;
    return 0;
}

int open_cfw_kvdb_write_menu_configuration(void)
{
    open_cfw_kvdb_module_menu_record *record =
        OPEN_CFW_KVDB_MODULE_MENU_RECORD;
    open_cfw_kvdb_module_runtime_menu_item *runtime =
        OPEN_CFW_KVDB_MODULE_RUNTIME_MENU;
    uint32_t count = OPEN_CFW_KVDB_MODULE_EXTERNAL_COUNT;
    uint32_t index;

    if (OPEN_CFW_KVDB_MODULE_USE_EXTERNAL != 1u || count < 1u) {
        OPEN_CFW_KVDB_MODULE_DIAGNOSTIC();
        return -1;
    }

    open_cfw_kvdb_module_zero(record, sizeof(*record));
    if (OPEN_CFW_KVDB_MODULE_READ(
            OPEN_CFW_KVDB_MODULE_MENU_KEY, record, sizeof(*record)
        ) > 0 && record->magic == OPEN_CFW_KVDB_MODULE_MENU_MAGIC &&
        record->count == count) {
        for (index = 0; index < count; ++index) {
            open_cfw_kvdb_module_menu_record_item *stored =
                &record->items[index];
            open_cfw_kvdb_module_runtime_menu_item *live = &runtime[index];
            if (stored->icon_num != live->icon_num ||
                stored->app_id != live->app_id ||
                stored->app_type != live->app_type ||
                open_cfw_kvdb_module_string_compare(
                    stored->text_name, live->text
                ) != 0) {
                break;
            }
        }
        if (index == count) {
            OPEN_CFW_KVDB_MODULE_DIAGNOSTIC();
            return 0;
        }
    }

    open_cfw_kvdb_module_zero(record, sizeof(*record));
    OPEN_CFW_KVDB_MODULE_SNAPSHOT_BEGIN();
    record->magic = OPEN_CFW_KVDB_MODULE_MENU_MAGIC;
    record->count = (uint8_t)count;
    for (index = 0; index < count; ++index) {
        open_cfw_kvdb_module_menu_record_item *stored = &record->items[index];
        open_cfw_kvdb_module_runtime_menu_item *live = &runtime[index];
        uint32_t length = open_cfw_kvdb_module_string_length(live->text);
        stored->icon_num = live->icon_num;
        stored->app_type = live->app_type;
        open_cfw_kvdb_module_copy(stored->text_name, live->text, length);
        stored->app_id = live->app_id;
    }
    OPEN_CFW_KVDB_MODULE_SNAPSHOT_END();
    OPEN_CFW_KVDB_MODULE_DIAGNOSTIC();
    return OPEN_CFW_KVDB_MODULE_WRITE(
        OPEN_CFW_KVDB_MODULE_MENU_KEY, record, sizeof(*record)
    );
}
