#include <string.h>

#include "kvdb_temperature_unit_host.h"

unsigned char open_cfw_test_kvdb_temperature_unit_record[12];
unsigned char open_cfw_test_kvdb_temperature_unit_read_value[12];
unsigned char open_cfw_test_kvdb_temperature_unit_written[12];
unsigned int open_cfw_test_kvdb_temperature_unit_write_count;
unsigned int open_cfw_test_kvdb_temperature_unit_diagnostic_count;
int open_cfw_test_kvdb_temperature_unit_read_result;

unsigned short open_cfw_test_kvdb_temperature_unit_crc16(
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

int open_cfw_test_kvdb_temperature_unit_read(
    const char *key,
    void *value,
    unsigned short length
)
{
    if (strcmp(key, "kvTemperatureUnit") != 0 || length != 12u) {
        return -9;
    }
    memcpy(value, open_cfw_test_kvdb_temperature_unit_read_value, 12u);
    return open_cfw_test_kvdb_temperature_unit_read_result;
}

int open_cfw_test_kvdb_temperature_unit_write(
    const char *key,
    const void *value,
    unsigned short length
)
{
    if (strcmp(key, "kvTemperatureUnit") != 0 || length != 12u) {
        return -9;
    }
    memcpy(open_cfw_test_kvdb_temperature_unit_written, value, 12u);
    ++open_cfw_test_kvdb_temperature_unit_write_count;
    return 0;
}

void open_cfw_test_kvdb_temperature_unit_diagnostic(void)
{
    ++open_cfw_test_kvdb_temperature_unit_diagnostic_count;
}

void open_cfw_test_kvdb_temperature_unit_set_read(
    const unsigned char *value,
    int result
)
{
    memcpy(open_cfw_test_kvdb_temperature_unit_read_value, value, 12u);
    open_cfw_test_kvdb_temperature_unit_read_result = result;
}

void open_cfw_test_kvdb_temperature_unit_reset(void)
{
    static const unsigned char defaults[12] = {
        1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    };
    memcpy(open_cfw_test_kvdb_temperature_unit_record, defaults, 12u);
    memset(open_cfw_test_kvdb_temperature_unit_read_value, 0, 12u);
    memset(open_cfw_test_kvdb_temperature_unit_written, 0, 12u);
    open_cfw_test_kvdb_temperature_unit_write_count = 0;
    open_cfw_test_kvdb_temperature_unit_diagnostic_count = 0;
    open_cfw_test_kvdb_temperature_unit_read_result = -1;
}
