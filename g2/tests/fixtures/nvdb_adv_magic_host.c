#include <string.h>

#include "nvdb_adv_magic_host.h"

unsigned char open_cfw_test_nvdb_adv_magic_record[4];
unsigned char open_cfw_test_nvdb_adv_magic_read_record[4];
unsigned char open_cfw_test_nvdb_adv_magic_written_record[4];
unsigned int open_cfw_test_nvdb_adv_magic_write_count;
unsigned int open_cfw_test_nvdb_adv_magic_last_write_length;
int open_cfw_test_nvdb_adv_magic_read_result;

unsigned short open_cfw_test_nvdb_adv_magic_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
)
{
    unsigned short crc = seed ? *seed : 0xFFFFu;
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

int open_cfw_test_nvdb_adv_magic_read(
    const char *key,
    void *value,
    unsigned short length
)
{
    if (strcmp(key, "nvAdvMagic") != 0 || length != 4u) {
        return -9;
    }
    memcpy(value, open_cfw_test_nvdb_adv_magic_read_record, 4u);
    return open_cfw_test_nvdb_adv_magic_read_result;
}

int open_cfw_test_nvdb_adv_magic_write(
    const char *key,
    const void *value,
    unsigned short length
)
{
    if (strcmp(key, "nvAdvMagic") != 0 || length != 4u) {
        return -9;
    }
    memcpy(open_cfw_test_nvdb_adv_magic_written_record, value, 4u);
    open_cfw_test_nvdb_adv_magic_last_write_length = length;
    ++open_cfw_test_nvdb_adv_magic_write_count;
    return 0;
}

void open_cfw_test_nvdb_adv_magic_reset(void)
{
    static const unsigned char defaults[4] = {1u, 0x20u, 0u, 0u};

    memcpy(open_cfw_test_nvdb_adv_magic_record, defaults, 4u);
    memset(open_cfw_test_nvdb_adv_magic_read_record, 0, 4u);
    memset(open_cfw_test_nvdb_adv_magic_written_record, 0, 4u);
    open_cfw_test_nvdb_adv_magic_write_count = 0u;
    open_cfw_test_nvdb_adv_magic_last_write_length = 0u;
    open_cfw_test_nvdb_adv_magic_read_result = 0;
}

void open_cfw_test_nvdb_adv_magic_set_read_record(
    const unsigned char *value,
    int result
)
{
    memcpy(open_cfw_test_nvdb_adv_magic_read_record, value, 4u);
    open_cfw_test_nvdb_adv_magic_read_result = result;
}
