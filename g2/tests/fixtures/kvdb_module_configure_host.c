#include <string.h>

#include "kvdb_module_configure_host.h"

uint32_t open_cfw_test_module_language;
uint32_t open_cfw_test_module_dashboard;
unsigned char open_cfw_test_module_record[888];
unsigned char open_cfw_test_module_runtime[52 * 20];
uint32_t open_cfw_test_module_use_external;
uint32_t open_cfw_test_module_external_count;
int open_cfw_test_module_read_result;
int open_cfw_test_module_write_result;
int open_cfw_test_module_dashboard_mode;
int open_cfw_test_module_lookup_result;
uint32_t open_cfw_test_module_lookup_id;
uint32_t open_cfw_test_module_read_count;
uint32_t open_cfw_test_module_write_count;
uint32_t open_cfw_test_module_begin_count;
uint32_t open_cfw_test_module_end_count;
uint32_t open_cfw_test_module_diagnostic_count;
char open_cfw_test_module_last_key[40];
uint16_t open_cfw_test_module_last_length;
unsigned char open_cfw_test_module_db_value[888];
unsigned char open_cfw_test_module_written[888];

int open_cfw_test_module_read(
    const char *key, void *value, uint16_t length
)
{
    strcpy(open_cfw_test_module_last_key, key);
    open_cfw_test_module_last_length = length;
    ++open_cfw_test_module_read_count;
    memcpy(value, open_cfw_test_module_db_value, length);
    return open_cfw_test_module_read_result;
}

int open_cfw_test_module_write(
    const char *key, const void *value, uint16_t length
)
{
    strcpy(open_cfw_test_module_last_key, key);
    open_cfw_test_module_last_length = length;
    ++open_cfw_test_module_write_count;
    memcpy(open_cfw_test_module_written, value, length);
    return open_cfw_test_module_write_result;
}

int open_cfw_test_module_mode(void)
{
    return open_cfw_test_module_dashboard_mode;
}

int open_cfw_test_module_lookup(
    uint32_t app_id, void *item, char *text, uint32_t *page, uint8_t *icon
)
{
    (void)item;
    open_cfw_test_module_lookup_id = app_id;
    if (open_cfw_test_module_lookup_result == 0) {
        memcpy(text, "builtin", 8u);
        *page = 0x1234u;
        *icon = 7u;
    }
    return open_cfw_test_module_lookup_result;
}

void open_cfw_test_module_snapshot_begin(void)
{
    ++open_cfw_test_module_begin_count;
}

void open_cfw_test_module_snapshot_end(void)
{
    ++open_cfw_test_module_end_count;
}

void open_cfw_test_module_diagnostic(void)
{
    ++open_cfw_test_module_diagnostic_count;
}

void open_cfw_test_module_reset(void)
{
    open_cfw_test_module_language = 6u;
    open_cfw_test_module_dashboard = 99u;
    memset(open_cfw_test_module_record, 0xa5, sizeof(open_cfw_test_module_record));
    memset(open_cfw_test_module_runtime, 0, sizeof(open_cfw_test_module_runtime));
    open_cfw_test_module_use_external = 0u;
    open_cfw_test_module_external_count = 0u;
    open_cfw_test_module_read_result = -1;
    open_cfw_test_module_write_result = 0;
    open_cfw_test_module_dashboard_mode = 0;
    open_cfw_test_module_lookup_result = 0;
    open_cfw_test_module_lookup_id = 0;
    open_cfw_test_module_read_count = 0;
    open_cfw_test_module_write_count = 0;
    open_cfw_test_module_begin_count = 0;
    open_cfw_test_module_end_count = 0;
    open_cfw_test_module_diagnostic_count = 0;
    memset(open_cfw_test_module_last_key, 0, sizeof(open_cfw_test_module_last_key));
    open_cfw_test_module_last_length = 0;
    memset(open_cfw_test_module_db_value, 0, sizeof(open_cfw_test_module_db_value));
    memset(open_cfw_test_module_written, 0, sizeof(open_cfw_test_module_written));
}
