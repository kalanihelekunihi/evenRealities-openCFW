#include <string.h>

#include "nvdb_sys_dt_host.h"

unsigned char open_cfw_test_nvdb_sys_dt_record[172];
unsigned char open_cfw_test_nvdb_sys_dt_otp_psn[15];
unsigned char open_cfw_test_nvdb_sys_dt_month_buffer[4];
unsigned char open_cfw_test_nvdb_sys_dt_legacy_psn_flag;
unsigned char open_cfw_test_nvdb_sys_dt_read_value[172];
unsigned char open_cfw_test_nvdb_sys_dt_written[172];
unsigned char open_cfw_test_nvdb_sys_dt_otp[8][16];
int open_cfw_test_nvdb_sys_dt_otp_read_status[8][4];
int open_cfw_test_nvdb_sys_dt_otp_write_status[4];
unsigned int open_cfw_test_nvdb_sys_dt_write_count;
unsigned int open_cfw_test_nvdb_sys_dt_last_write_length;
unsigned int open_cfw_test_nvdb_sys_dt_otp_begin_count;
unsigned int open_cfw_test_nvdb_sys_dt_otp_end_count;
unsigned int open_cfw_test_nvdb_sys_dt_otp_write_count;
unsigned int open_cfw_test_nvdb_sys_dt_parse_count;
unsigned int open_cfw_test_nvdb_sys_dt_diagnostic_count;
unsigned int open_cfw_test_nvdb_sys_dt_parsed_year;
int open_cfw_test_nvdb_sys_dt_read_result;
char open_cfw_test_nvdb_sys_dt_parsed_project[5];
char open_cfw_test_nvdb_sys_dt_parsed_manufacturer[20];
char open_cfw_test_nvdb_sys_dt_parsed_month[4];
char open_cfw_test_nvdb_sys_dt_parsed_day[3];
char open_cfw_test_nvdb_sys_dt_parsed_serial[5];
char open_cfw_test_nvdb_sys_dt_parsed_codes[4];

static const unsigned char open_cfw_test_nvdb_sys_dt_defaults[172] = {
    0x02,0x53,0x32,0x30,0x30,0x4c,0x44,0x42,0x45,0x32,0x31,0x30,
    0x30,0x30,0x31,0x00,0x53,0x32,0x30,0x30,0x45,0x56,0x42,0x54,
    0x4c,0x4e,0x32,0x35,0x30,0x36,0x33,0x30,0x31,0x31,0x31,0x31,
    0x31,0x00,0x00,0x00,0x69,0x34,0x01,0x00,0x0c,0x0a,0x0f,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,
};

unsigned short open_cfw_test_nvdb_sys_dt_crc16(
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

int open_cfw_test_nvdb_sys_dt_read(
    const char *key,
    void *value,
    unsigned short length
)
{
    if (strcmp(key, "nvSysDt") != 0 || length != 172u) {
        return -9;
    }
    memcpy(value, open_cfw_test_nvdb_sys_dt_read_value, 172u);
    return open_cfw_test_nvdb_sys_dt_read_result;
}

int open_cfw_test_nvdb_sys_dt_write(
    const char *key,
    const void *value,
    unsigned short length
)
{
    if (strcmp(key, "nvSysDt") != 0 || length != 172u) {
        return -9;
    }
    memcpy(open_cfw_test_nvdb_sys_dt_written, value, 172u);
    open_cfw_test_nvdb_sys_dt_last_write_length = length;
    ++open_cfw_test_nvdb_sys_dt_write_count;
    return 0;
}

void open_cfw_test_nvdb_sys_dt_otp_begin(void)
{
    ++open_cfw_test_nvdb_sys_dt_otp_begin_count;
}

void open_cfw_test_nvdb_sys_dt_otp_end(void)
{
    ++open_cfw_test_nvdb_sys_dt_otp_end_count;
}

int open_cfw_test_nvdb_sys_dt_otp_read_word(
    unsigned int offset,
    unsigned int *value
)
{
    unsigned int relative;
    unsigned int slot;
    unsigned int word;

    if (offset < 0x340u || offset >= 0x3c0u || (offset & 3u) != 0u) {
        return -8;
    }
    relative = offset - 0x340u;
    slot = relative / 16u;
    word = (relative % 16u) / 4u;
    memcpy(value, &open_cfw_test_nvdb_sys_dt_otp[slot][word * 4u], 4u);
    return open_cfw_test_nvdb_sys_dt_otp_read_status[slot][word];
}

int open_cfw_test_nvdb_sys_dt_otp_write_word(
    unsigned int offset,
    unsigned int value
)
{
    unsigned int relative;
    unsigned int slot;
    unsigned int word;
    int status;

    if (offset < 0x340u || offset >= 0x3c0u || (offset & 3u) != 0u) {
        return -8;
    }
    relative = offset - 0x340u;
    slot = relative / 16u;
    word = (relative % 16u) / 4u;
    status = open_cfw_test_nvdb_sys_dt_otp_write_status[word];
    if (status == 0) {
        memcpy(&open_cfw_test_nvdb_sys_dt_otp[slot][word * 4u], &value, 4u);
        ++open_cfw_test_nvdb_sys_dt_otp_write_count;
    }
    return status;
}

void open_cfw_test_nvdb_sys_dt_parsed(
    const char *project_code,
    char manufacturer_code,
    const char *manufacturer,
    char color,
    char year_code,
    unsigned int year,
    char month_code,
    const char *month,
    const char *day,
    const char *serial_number
)
{
    ++open_cfw_test_nvdb_sys_dt_parse_count;
    strcpy(open_cfw_test_nvdb_sys_dt_parsed_project, project_code);
    strcpy(open_cfw_test_nvdb_sys_dt_parsed_manufacturer, manufacturer);
    strcpy(open_cfw_test_nvdb_sys_dt_parsed_month, month);
    strcpy(open_cfw_test_nvdb_sys_dt_parsed_day, day);
    strcpy(open_cfw_test_nvdb_sys_dt_parsed_serial, serial_number);
    open_cfw_test_nvdb_sys_dt_parsed_codes[0] = manufacturer_code;
    open_cfw_test_nvdb_sys_dt_parsed_codes[1] = color;
    open_cfw_test_nvdb_sys_dt_parsed_codes[2] = year_code;
    open_cfw_test_nvdb_sys_dt_parsed_codes[3] = month_code;
    open_cfw_test_nvdb_sys_dt_parsed_year = year;
}

void open_cfw_test_nvdb_sys_dt_diagnostic(void)
{
    ++open_cfw_test_nvdb_sys_dt_diagnostic_count;
}

void open_cfw_test_nvdb_sys_dt_reset(void)
{
    memcpy(open_cfw_test_nvdb_sys_dt_record,
        open_cfw_test_nvdb_sys_dt_defaults, 172u);
    memset(open_cfw_test_nvdb_sys_dt_otp_psn, 0, 15u);
    memset(open_cfw_test_nvdb_sys_dt_month_buffer, 0, 4u);
    memset(open_cfw_test_nvdb_sys_dt_read_value, 0, 172u);
    memset(open_cfw_test_nvdb_sys_dt_written, 0, 172u);
    memset(open_cfw_test_nvdb_sys_dt_otp, 0xff,
        sizeof(open_cfw_test_nvdb_sys_dt_otp));
    memset(open_cfw_test_nvdb_sys_dt_otp_read_status, 0,
        sizeof(open_cfw_test_nvdb_sys_dt_otp_read_status));
    memset(open_cfw_test_nvdb_sys_dt_otp_write_status, 0,
        sizeof(open_cfw_test_nvdb_sys_dt_otp_write_status));
    memset(open_cfw_test_nvdb_sys_dt_parsed_project, 0, 5u);
    memset(open_cfw_test_nvdb_sys_dt_parsed_manufacturer, 0, 20u);
    memset(open_cfw_test_nvdb_sys_dt_parsed_month, 0, 4u);
    memset(open_cfw_test_nvdb_sys_dt_parsed_day, 0, 3u);
    memset(open_cfw_test_nvdb_sys_dt_parsed_serial, 0, 5u);
    memset(open_cfw_test_nvdb_sys_dt_parsed_codes, 0, 4u);
    open_cfw_test_nvdb_sys_dt_legacy_psn_flag = 0u;
    open_cfw_test_nvdb_sys_dt_write_count = 0u;
    open_cfw_test_nvdb_sys_dt_last_write_length = 0u;
    open_cfw_test_nvdb_sys_dt_otp_begin_count = 0u;
    open_cfw_test_nvdb_sys_dt_otp_end_count = 0u;
    open_cfw_test_nvdb_sys_dt_otp_write_count = 0u;
    open_cfw_test_nvdb_sys_dt_parse_count = 0u;
    open_cfw_test_nvdb_sys_dt_diagnostic_count = 0u;
    open_cfw_test_nvdb_sys_dt_parsed_year = 0u;
    open_cfw_test_nvdb_sys_dt_read_result = 0;
}

void open_cfw_test_nvdb_sys_dt_set_read(
    const unsigned char *value,
    int result
)
{
    memcpy(open_cfw_test_nvdb_sys_dt_read_value, value, 172u);
    open_cfw_test_nvdb_sys_dt_read_result = result;
}

void open_cfw_test_nvdb_sys_dt_set_otp_slot(
    unsigned int slot,
    const unsigned char *value
)
{
    if (slot < 8u) {
        memcpy(open_cfw_test_nvdb_sys_dt_otp[slot], value, 16u);
    }
}

void open_cfw_test_nvdb_sys_dt_set_otp_read_failure(
    unsigned int slot,
    unsigned int word,
    int status
)
{
    if (slot < 8u && word < 4u) {
        open_cfw_test_nvdb_sys_dt_otp_read_status[slot][word] = status;
    }
}

void open_cfw_test_nvdb_sys_dt_set_otp_write_failure(
    unsigned int word,
    int status
)
{
    if (word < 4u) {
        open_cfw_test_nvdb_sys_dt_otp_write_status[word] = status;
    }
}
