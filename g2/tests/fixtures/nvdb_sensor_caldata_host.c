#include <string.h>

#include "nvdb_sensor_caldata_host.h"

unsigned char open_cfw_test_nvdb_sensor_caldata_record[92];
unsigned char open_cfw_test_nvdb_sensor_caldata_ag_record[68];
unsigned char open_cfw_test_nvdb_sensor_caldata_read_primary[92];
unsigned char open_cfw_test_nvdb_sensor_caldata_read_ag[68];
unsigned char open_cfw_test_nvdb_sensor_caldata_written[92];
unsigned int open_cfw_test_nvdb_sensor_caldata_write_count;
unsigned int open_cfw_test_nvdb_sensor_caldata_last_write_length;
unsigned int open_cfw_test_nvdb_sensor_caldata_diagnostic_count;
int open_cfw_test_nvdb_sensor_caldata_read_primary_result;
int open_cfw_test_nvdb_sensor_caldata_read_ag_result;
int open_cfw_test_nvdb_sensor_caldata_pattern_enabled;

static const unsigned char open_cfw_test_primary_defaults[92] = {
    0x01,0x00,0x00,0x00,0x00,0x00,0xa0,0x3f,0x00,0x00,0xa0,0x3f,
    0x00,0x00,0xa0,0x3f,0x00,0x00,0xa0,0x3f,0x00,0x00,0xa0,0x3f,
    0x00,0x00,0xa0,0x3f,0x00,0x00,0xa0,0x3f,0x00,0x00,0xa0,0x3f,
    0x00,0x00,0xa0,0x3f,0x00,0x00,0xa0,0x3f,0x79,0x29,0xed,0xff,
    0x87,0xd6,0x12,0x00,0x87,0xd6,0x12,0x00,0x79,0x29,0xed,0xff,
    0x00,0x00,0xa0,0x3f,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,
    0xff,0xff,0xff,0xff,0x00,0x00,0x00,0x00,
};
static const unsigned char open_cfw_test_ag_defaults[68] = {
    0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x4b,0xab,0x51,0xbf,0x99,0xd5,0xbb,0xbe,
    0xfd,0x12,0xd9,0x3e,0xcb,0x48,0xe5,0x3e,0xff,0x0c,0x8a,0x3d,
    0x02,0x80,0x5f,0x3f,0x4a,0xd1,0xb2,0xbe,0x88,0xd6,0x6e,0x3f,
    0x84,0x9e,0xed,0x3d,0x00,0x00,0x00,0x00,
};

unsigned short open_cfw_test_nvdb_sensor_caldata_crc16(
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

int open_cfw_test_nvdb_sensor_caldata_read(
    const char *key,
    void *value,
    unsigned short length
)
{
    if (strcmp(key, "nvSCald") == 0 && length == 92u) {
        memcpy(value, open_cfw_test_nvdb_sensor_caldata_read_primary, 92u);
        return open_cfw_test_nvdb_sensor_caldata_read_primary_result;
    }
    if (strcmp(key, "nvSCaldAG") == 0 && length == 68u) {
        memcpy(value, open_cfw_test_nvdb_sensor_caldata_read_ag, 68u);
        return open_cfw_test_nvdb_sensor_caldata_read_ag_result;
    }
    return -9;
}

int open_cfw_test_nvdb_sensor_caldata_write(
    const char *key,
    const void *value,
    unsigned short length
)
{
    if ((strcmp(key, "nvSCald") != 0 || length != 92u) &&
        (strcmp(key, "nvSCaldAG") != 0 || length != 68u)) {
        return -9;
    }
    memset(open_cfw_test_nvdb_sensor_caldata_written, 0, 92u);
    memcpy(open_cfw_test_nvdb_sensor_caldata_written, value, length);
    open_cfw_test_nvdb_sensor_caldata_last_write_length = length;
    ++open_cfw_test_nvdb_sensor_caldata_write_count;
    return 0;
}

int open_cfw_test_nvdb_sensor_caldata_pattern_check_enabled(void)
{
    return open_cfw_test_nvdb_sensor_caldata_pattern_enabled;
}

void open_cfw_test_nvdb_sensor_caldata_diagnostic(void)
{
    ++open_cfw_test_nvdb_sensor_caldata_diagnostic_count;
}

void open_cfw_test_nvdb_sensor_caldata_reset(void)
{
    memcpy(open_cfw_test_nvdb_sensor_caldata_record,
        open_cfw_test_primary_defaults, 92u);
    memcpy(open_cfw_test_nvdb_sensor_caldata_ag_record,
        open_cfw_test_ag_defaults, 68u);
    memset(open_cfw_test_nvdb_sensor_caldata_read_primary, 0, 92u);
    memset(open_cfw_test_nvdb_sensor_caldata_read_ag, 0, 68u);
    memset(open_cfw_test_nvdb_sensor_caldata_written, 0, 92u);
    open_cfw_test_nvdb_sensor_caldata_write_count = 0u;
    open_cfw_test_nvdb_sensor_caldata_last_write_length = 0u;
    open_cfw_test_nvdb_sensor_caldata_diagnostic_count = 0u;
    open_cfw_test_nvdb_sensor_caldata_read_primary_result = 0;
    open_cfw_test_nvdb_sensor_caldata_read_ag_result = 0;
    open_cfw_test_nvdb_sensor_caldata_pattern_enabled = 1;
}

void open_cfw_test_nvdb_sensor_caldata_set_read(
    const char *key,
    const unsigned char *value,
    int result
)
{
    if (strcmp(key, "nvSCald") == 0) {
        memcpy(open_cfw_test_nvdb_sensor_caldata_read_primary, value, 92u);
        open_cfw_test_nvdb_sensor_caldata_read_primary_result = result;
    } else {
        memcpy(open_cfw_test_nvdb_sensor_caldata_read_ag, value, 68u);
        open_cfw_test_nvdb_sensor_caldata_read_ag_result = result;
    }
}

void open_cfw_test_nvdb_sensor_caldata_set_pattern_check(int enabled)
{
    open_cfw_test_nvdb_sensor_caldata_pattern_enabled = enabled;
}
