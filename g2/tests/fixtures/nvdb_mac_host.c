#include <string.h>

#include "nvdb_mac_host.h"

unsigned char open_cfw_test_nvdb_mac_record[10];
unsigned char open_cfw_test_nvdb_mac_read_record[10];
unsigned char open_cfw_test_nvdb_mac_written_record[10];
unsigned int open_cfw_test_nvdb_mac_write_count;
unsigned int open_cfw_test_nvdb_mac_diagnostic_count;
unsigned int open_cfw_test_nvdb_mac_last_write_length;
unsigned int open_cfw_test_nvdb_mac_chip_id0;
unsigned int open_cfw_test_nvdb_mac_chip_id1;
int open_cfw_test_nvdb_mac_read_result;

void open_cfw_test_nvdb_mac_device_ids_get(
    unsigned int *chip_id0,
    unsigned int *chip_id1
)
{
    *chip_id0 = open_cfw_test_nvdb_mac_chip_id0;
    *chip_id1 = open_cfw_test_nvdb_mac_chip_id1;
}

unsigned int open_cfw_test_nvdb_mac_crc32(
    const unsigned char *data,
    unsigned int length,
    const unsigned int *seed
)
{
    unsigned int crc = seed ? ~*seed : 0xFFFFFFFFu;
    unsigned int index;
    unsigned int bit;

    for (index = 0; index < length; ++index) {
        crc ^= data[index];
        for (bit = 0; bit < 8u; ++bit) {
            crc = (crc & 1u) != 0u
                ? (crc >> 1u) ^ 0xEDB88320u
                : crc >> 1u;
        }
    }
    return ~crc;
}

unsigned short open_cfw_test_nvdb_mac_crc16(
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

int open_cfw_test_nvdb_mac_read(
    const char *key,
    void *value,
    unsigned short length
)
{
    if (strcmp(key, "nvMAC") != 0 || length != 10u) {
        return -9;
    }
    memcpy(value, open_cfw_test_nvdb_mac_read_record, 10u);
    return open_cfw_test_nvdb_mac_read_result;
}

int open_cfw_test_nvdb_mac_write(
    const char *key,
    const void *value,
    unsigned short length
)
{
    if (strcmp(key, "nvMAC") != 0 || length != 10u) {
        return -9;
    }
    memcpy(open_cfw_test_nvdb_mac_written_record, value, 10u);
    open_cfw_test_nvdb_mac_last_write_length = length;
    ++open_cfw_test_nvdb_mac_write_count;
    return 0;
}

void open_cfw_test_nvdb_mac_diagnostic(void)
{
    ++open_cfw_test_nvdb_mac_diagnostic_count;
}

void open_cfw_test_nvdb_mac_reset(void)
{
    static const unsigned char defaults[10] = {
        1u, 0u, 0u, 0u, 0u, 0u, 0u, 0u, 0u, 0u
    };

    memcpy(open_cfw_test_nvdb_mac_record, defaults, 10u);
    memset(open_cfw_test_nvdb_mac_read_record, 0, 10u);
    memset(open_cfw_test_nvdb_mac_written_record, 0, 10u);
    open_cfw_test_nvdb_mac_write_count = 0u;
    open_cfw_test_nvdb_mac_diagnostic_count = 0u;
    open_cfw_test_nvdb_mac_last_write_length = 0u;
    open_cfw_test_nvdb_mac_chip_id0 = 0x01234567u;
    open_cfw_test_nvdb_mac_chip_id1 = 0x89ABCDEFu;
    open_cfw_test_nvdb_mac_read_result = 0;
}

void open_cfw_test_nvdb_mac_set_device_ids(
    unsigned int chip_id0,
    unsigned int chip_id1
)
{
    open_cfw_test_nvdb_mac_chip_id0 = chip_id0;
    open_cfw_test_nvdb_mac_chip_id1 = chip_id1;
}

void open_cfw_test_nvdb_mac_set_read_record(
    const unsigned char *value,
    int result
)
{
    memcpy(open_cfw_test_nvdb_mac_read_record, value, 10u);
    open_cfw_test_nvdb_mac_read_result = result;
}
