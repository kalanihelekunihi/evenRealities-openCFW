#include <string.h>

#include "kvdb_ring_host.h"

unsigned char open_cfw_test_kvdb_ring_record[24];
unsigned char open_cfw_test_kvdb_ring_read_value[24];
unsigned char open_cfw_test_kvdb_ring_written[24];
unsigned int open_cfw_test_kvdb_ring_write_count;
unsigned int open_cfw_test_kvdb_ring_diagnostic_count;
int open_cfw_test_kvdb_ring_read_result;

unsigned short open_cfw_test_kvdb_ring_crc16(
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

int open_cfw_test_kvdb_ring_read(
    const char *key, void *value, unsigned short length
)
{
    if (strcmp(key, "kvRing") != 0 || length != 24u) {
        return -9;
    }
    memcpy(value, open_cfw_test_kvdb_ring_read_value, 24u);
    return open_cfw_test_kvdb_ring_read_result;
}

int open_cfw_test_kvdb_ring_write(
    const char *key, const void *value, unsigned short length
)
{
    if (strcmp(key, "kvRing") != 0 || length != 24u) {
        return -9;
    }
    memcpy(open_cfw_test_kvdb_ring_written, value, 24u);
    ++open_cfw_test_kvdb_ring_write_count;
    return 0;
}

void open_cfw_test_kvdb_ring_diagnostic(void)
{
    ++open_cfw_test_kvdb_ring_diagnostic_count;
}

void open_cfw_test_kvdb_ring_set_read(const unsigned char *value, int result)
{
    memcpy(open_cfw_test_kvdb_ring_read_value, value, 24u);
    open_cfw_test_kvdb_ring_read_result = result;
}

void open_cfw_test_kvdb_ring_reset(void)
{
    static const unsigned char defaults[24] = {
        1, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
        'E', 'V', 'E', 'N', ' ', 'R', '1', '_',
        'F', 'F', 'F', 'F', 'F', 'F', 0, 0, 0,
    };
    memcpy(open_cfw_test_kvdb_ring_record, defaults, 24u);
    memset(open_cfw_test_kvdb_ring_read_value, 0, 24u);
    memset(open_cfw_test_kvdb_ring_written, 0, 24u);
    open_cfw_test_kvdb_ring_write_count = 0;
    open_cfw_test_kvdb_ring_diagnostic_count = 0;
    open_cfw_test_kvdb_ring_read_result = -1;
}
