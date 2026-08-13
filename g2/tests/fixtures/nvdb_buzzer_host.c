#include <string.h>

#include "nvdb_buzzer_host.h"

unsigned char open_cfw_test_nvdb_buzzer_record[12];
unsigned char open_cfw_test_nvdb_buzzer_read_record[12];
unsigned char open_cfw_test_nvdb_buzzer_written_record[12];
unsigned int open_cfw_test_nvdb_buzzer_write_count;
unsigned int open_cfw_test_nvdb_buzzer_diagnostic_count;
unsigned int open_cfw_test_nvdb_buzzer_last_write_length;
int open_cfw_test_nvdb_buzzer_read_result;

unsigned short open_cfw_test_nvdb_buzzer_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
)
{
    unsigned short crc = seed ? *seed : 0xFFFFu;
    unsigned int i;
    unsigned int bit;

    for (i = 0; i < length; ++i) {
        crc ^= (unsigned short)((unsigned short)data[i] << 8);
        for (bit = 0; bit < 8; ++bit) {
            crc = (unsigned short)((crc & 0x8000u) != 0u
                ? (unsigned short)((crc << 1) ^ 0x1021u)
                : (unsigned short)(crc << 1));
        }
    }
    return crc;
}

int open_cfw_test_nvdb_buzzer_read(
    const char *key,
    void *value,
    unsigned short length
)
{
    if (strcmp(key, "nvBuzzer") != 0 || length != 12u) {
        return -9;
    }
    memcpy(value, open_cfw_test_nvdb_buzzer_read_record, 12u);
    return open_cfw_test_nvdb_buzzer_read_result;
}

int open_cfw_test_nvdb_buzzer_write(
    const char *key,
    const void *value,
    unsigned short length
)
{
    if (strcmp(key, "nvBuzzer") != 0 || length != 12u) {
        return -9;
    }
    memcpy(open_cfw_test_nvdb_buzzer_written_record, value, 12u);
    open_cfw_test_nvdb_buzzer_last_write_length = length;
    ++open_cfw_test_nvdb_buzzer_write_count;
    return 0;
}

void open_cfw_test_nvdb_buzzer_diagnostic(void)
{
    ++open_cfw_test_nvdb_buzzer_diagnostic_count;
}

void open_cfw_test_nvdb_buzzer_reset(void)
{
    static const unsigned char defaults[12] = {
        2u, 0u, 0u, 0u, 0xA0u, 0x0Fu, 0u, 0u, 30u, 0u, 0u, 0u
    };

    memcpy(open_cfw_test_nvdb_buzzer_record, defaults, 12u);
    memset(open_cfw_test_nvdb_buzzer_read_record, 0, 12u);
    memset(open_cfw_test_nvdb_buzzer_written_record, 0, 12u);
    open_cfw_test_nvdb_buzzer_write_count = 0u;
    open_cfw_test_nvdb_buzzer_diagnostic_count = 0u;
    open_cfw_test_nvdb_buzzer_last_write_length = 0u;
    open_cfw_test_nvdb_buzzer_read_result = 0;
}

void open_cfw_test_nvdb_buzzer_set_read_record(
    const unsigned char *value,
    int result
)
{
    memcpy(open_cfw_test_nvdb_buzzer_read_record, value, 12u);
    open_cfw_test_nvdb_buzzer_read_result = result;
}
