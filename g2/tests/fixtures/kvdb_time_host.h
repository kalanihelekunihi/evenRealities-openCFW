#ifndef OPEN_CFW_KVDB_TIME_HOST_H
#define OPEN_CFW_KVDB_TIME_HOST_H

extern unsigned char open_cfw_test_kvdb_time_record[12];
extern unsigned char open_cfw_test_kvdb_time_read_value[12];
extern unsigned char open_cfw_test_kvdb_time_written[12];
extern unsigned int open_cfw_test_kvdb_time_write_count;
extern unsigned int open_cfw_test_kvdb_time_diagnostic_count;
extern int open_cfw_test_kvdb_time_read_result;

void open_cfw_test_kvdb_time_reset(void);
void open_cfw_test_kvdb_time_set_read(const unsigned char *value, int result);
unsigned short open_cfw_test_kvdb_time_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
);
int open_cfw_test_kvdb_time_read(
    const char *key, void *value, unsigned short length
);
int open_cfw_test_kvdb_time_write(
    const char *key, const void *value, unsigned short length
);
void open_cfw_test_kvdb_time_diagnostic(void);

#define OPEN_CFW_KVDB_TIME_RECORD_ADDRESS \
    ((unsigned long)open_cfw_test_kvdb_time_record)
#define OPEN_CFW_KVDB_TIME_CRC16(data, length, seed) \
    open_cfw_test_kvdb_time_crc16((data), (length), (seed))
#define OPEN_CFW_KVDB_TIME_READ(key, value, length) \
    open_cfw_test_kvdb_time_read((key), (value), (length))
#define OPEN_CFW_KVDB_TIME_WRITE(key, value, length) \
    open_cfw_test_kvdb_time_write((key), (value), (length))
#define OPEN_CFW_KVDB_TIME_DIAGNOSTIC() open_cfw_test_kvdb_time_diagnostic()

#endif
