#ifndef OPEN_CFW_KVDB_MODULE_CONFIGURE_HOST_H
#define OPEN_CFW_KVDB_MODULE_CONFIGURE_HOST_H

#include <stdint.h>

extern uint32_t open_cfw_test_module_language;
extern uint32_t open_cfw_test_module_dashboard;
extern unsigned char open_cfw_test_module_record[888];
extern unsigned char open_cfw_test_module_runtime[52 * 20];
extern uint32_t open_cfw_test_module_use_external;
extern uint32_t open_cfw_test_module_external_count;

int open_cfw_test_module_read(const char *, void *, uint16_t);
int open_cfw_test_module_write(const char *, const void *, uint16_t);
int open_cfw_test_module_mode(void);
int open_cfw_test_module_lookup(
    uint32_t, void *, char *, uint32_t *, uint8_t *
);
void open_cfw_test_module_snapshot_begin(void);
void open_cfw_test_module_snapshot_end(void);
void open_cfw_test_module_diagnostic(void);

#define OPEN_CFW_KVDB_MODULE_LANGUAGE_ADDRESS \
    ((uintptr_t)&open_cfw_test_module_language)
#define OPEN_CFW_KVDB_MODULE_DASHBOARD_ADDRESS \
    ((uintptr_t)&open_cfw_test_module_dashboard)
#define OPEN_CFW_KVDB_MODULE_MENU_RECORD_ADDRESS \
    ((uintptr_t)open_cfw_test_module_record)
#define OPEN_CFW_KVDB_MODULE_RUNTIME_MENU_ADDRESS \
    ((uintptr_t)open_cfw_test_module_runtime)
#define OPEN_CFW_KVDB_MODULE_USE_EXTERNAL_ADDRESS \
    ((uintptr_t)&open_cfw_test_module_use_external)
#define OPEN_CFW_KVDB_MODULE_EXTERNAL_COUNT_ADDRESS \
    ((uintptr_t)&open_cfw_test_module_external_count)
#define OPEN_CFW_KVDB_MODULE_CUSTOM_RESOURCE_ADDRESS \
    0x76543210u
#define OPEN_CFW_KVDB_MODULE_READ(key, value, length) \
    open_cfw_test_module_read((key), (value), (length))
#define OPEN_CFW_KVDB_MODULE_WRITE(key, value, length) \
    open_cfw_test_module_write((key), (value), (length))
#define OPEN_CFW_KVDB_MODULE_DASHBOARD_MODE() open_cfw_test_module_mode()
#define OPEN_CFW_KVDB_MODULE_LOOKUP_BUILTIN(id, item, text, page, icon) \
    open_cfw_test_module_lookup((id), (item), (text), (page), (icon))
#define OPEN_CFW_KVDB_MODULE_SNAPSHOT_BEGIN() \
    open_cfw_test_module_snapshot_begin()
#define OPEN_CFW_KVDB_MODULE_SNAPSHOT_END() open_cfw_test_module_snapshot_end()
#define OPEN_CFW_KVDB_MODULE_DIAGNOSTIC() open_cfw_test_module_diagnostic()

extern int open_cfw_test_module_read_result;
extern int open_cfw_test_module_write_result;
extern int open_cfw_test_module_dashboard_mode;
extern int open_cfw_test_module_lookup_result;
extern uint32_t open_cfw_test_module_lookup_id;
extern uint32_t open_cfw_test_module_read_count;
extern uint32_t open_cfw_test_module_write_count;
extern uint32_t open_cfw_test_module_begin_count;
extern uint32_t open_cfw_test_module_end_count;
extern uint32_t open_cfw_test_module_diagnostic_count;
extern char open_cfw_test_module_last_key[40];
extern uint16_t open_cfw_test_module_last_length;
extern unsigned char open_cfw_test_module_db_value[888];
extern unsigned char open_cfw_test_module_written[888];

void open_cfw_test_module_reset(void);

#endif
