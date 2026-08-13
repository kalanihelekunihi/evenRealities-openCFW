#include <string.h>

#include "kvdb_universal_setting_host.h"

unsigned char open_cfw_test_kvdb_universal_setting_record[20];
unsigned char open_cfw_test_kvdb_universal_setting_read_value[20];
unsigned char open_cfw_test_kvdb_universal_setting_written[20];
unsigned int open_cfw_test_kvdb_universal_setting_write_count;
unsigned int open_cfw_test_kvdb_universal_setting_diagnostic_count;
int open_cfw_test_kvdb_universal_setting_read_result;

unsigned short open_cfw_test_kvdb_universal_setting_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
)
{
    unsigned short crc = seed ? *seed : 0xffffu;
    unsigned int index;
    unsigned int bit;

    for (index = 0; index < length; ++index) {
        crc ^= (unsigned short)((unsigned short)data[index] << 8);
        for (bit = 0; bit < 8u; ++bit) {
            crc = (unsigned short)((crc & 0x8000u) != 0u
                ? (unsigned short)((crc << 1u) ^ 0x1021u)
                : (unsigned short)(crc << 1u));
        }
    }
    return crc;
}

int open_cfw_test_kvdb_universal_setting_read(
    const char *key,
    void *value,
    unsigned short length
)
{
    if (strcmp(key, "kvUniversalSetting") != 0 || length != 20u) {
        return -9;
    }
    memcpy(value, open_cfw_test_kvdb_universal_setting_read_value, 20u);
    return open_cfw_test_kvdb_universal_setting_read_result;
}

int open_cfw_test_kvdb_universal_setting_write(
    const char *key,
    const void *value,
    unsigned short length
)
{
    if (strcmp(key, "kvUniversalSetting") != 0 || length != 20u) {
        return -9;
    }
    memcpy(open_cfw_test_kvdb_universal_setting_written, value, 20u);
    ++open_cfw_test_kvdb_universal_setting_write_count;
    return 0;
}

void open_cfw_test_kvdb_universal_setting_diagnostic(void)
{
    ++open_cfw_test_kvdb_universal_setting_diagnostic_count;
}

void open_cfw_test_kvdb_universal_setting_set_read(
    const unsigned char *value,
    int result
)
{
    memcpy(open_cfw_test_kvdb_universal_setting_read_value, value, 20u);
    open_cfw_test_kvdb_universal_setting_read_result = result;
}

void open_cfw_test_kvdb_universal_setting_reset(void)
{
    static const unsigned char defaults[20] = {
        3, 0, 0, 0, 1, 0, 0, 0, 0, 0,
        0, 0, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0, 0,
    };
    memcpy(open_cfw_test_kvdb_universal_setting_record, defaults, 20u);
    memset(open_cfw_test_kvdb_universal_setting_read_value, 0, 20u);
    memset(open_cfw_test_kvdb_universal_setting_written, 0, 20u);
    open_cfw_test_kvdb_universal_setting_write_count = 0;
    open_cfw_test_kvdb_universal_setting_diagnostic_count = 0;
    open_cfw_test_kvdb_universal_setting_read_result = -1;
}
