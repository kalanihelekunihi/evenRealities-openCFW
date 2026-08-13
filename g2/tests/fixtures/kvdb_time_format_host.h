#ifndef OPEN_CFW_KVDB_TIME_FORMAT_HOST_H
#define OPEN_CFW_KVDB_TIME_FORMAT_HOST_H

extern unsigned char open_cfw_test_kvdb_time_format_record[12];
extern unsigned char open_cfw_test_kvdb_time_format_read_value[12];
extern unsigned char open_cfw_test_kvdb_time_format_written[12];
extern unsigned int open_cfw_test_kvdb_time_format_write_count;
extern unsigned int open_cfw_test_kvdb_time_format_diagnostic_count;
extern int open_cfw_test_kvdb_time_format_read_result;

void open_cfw_test_kvdb_time_format_reset(void);
void open_cfw_test_kvdb_time_format_set_read(
    const unsigned char *value,
    int result
);

unsigned short open_cfw_test_kvdb_time_format_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
);
int open_cfw_test_kvdb_time_format_read(
    const char *key,
    void *value,
    unsigned short length
);
int open_cfw_test_kvdb_time_format_write(
    const char *key,
    const void *value,
    unsigned short length
);
void open_cfw_test_kvdb_time_format_diagnostic(void);

#define OPEN_CFW_KVDB_TIME_FORMAT_RECORD_ADDRESS \
    ((unsigned long)open_cfw_test_kvdb_time_format_record)
#define OPEN_CFW_KVDB_TIME_FORMAT_CRC16(data, length, seed) \
    open_cfw_test_kvdb_time_format_crc16((data), (length), (seed))
#define OPEN_CFW_KVDB_TIME_FORMAT_READ(key, value, length) \
    open_cfw_test_kvdb_time_format_read((key), (value), (length))
#define OPEN_CFW_KVDB_TIME_FORMAT_WRITE(key, value, length) \
    open_cfw_test_kvdb_time_format_write((key), (value), (length))
#define OPEN_CFW_KVDB_TIME_FORMAT_DIAGNOSTIC() \
    open_cfw_test_kvdb_time_format_diagnostic()

#endif
