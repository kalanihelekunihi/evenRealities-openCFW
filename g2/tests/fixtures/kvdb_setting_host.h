#ifndef OPEN_CFW_KVDB_SETTING_HOST_H
#define OPEN_CFW_KVDB_SETTING_HOST_H

extern unsigned char open_cfw_test_kvdb_setting_record[28];
extern unsigned char open_cfw_test_kvdb_setting_read_value[28];
extern unsigned char open_cfw_test_kvdb_setting_written[28];
extern unsigned int open_cfw_test_kvdb_setting_write_count;
extern unsigned int open_cfw_test_kvdb_setting_diagnostic_count;
extern int open_cfw_test_kvdb_setting_read_result;

void open_cfw_test_kvdb_setting_reset(void);
void open_cfw_test_kvdb_setting_set_read(const unsigned char *value, int result);
unsigned short open_cfw_test_kvdb_setting_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
);
int open_cfw_test_kvdb_setting_read(
    const char *key,
    void *value,
    unsigned short length
);
int open_cfw_test_kvdb_setting_write(
    const char *key,
    const void *value,
    unsigned short length
);
void open_cfw_test_kvdb_setting_diagnostic(void);

#define OPEN_CFW_KVDB_SETTING_RECORD_ADDRESS \
    ((unsigned long)open_cfw_test_kvdb_setting_record)
#define OPEN_CFW_KVDB_SETTING_CRC16(data, length, seed) \
    open_cfw_test_kvdb_setting_crc16((data), (length), (seed))
#define OPEN_CFW_KVDB_SETTING_READ(key, value, length) \
    open_cfw_test_kvdb_setting_read((key), (value), (length))
#define OPEN_CFW_KVDB_SETTING_WRITE(key, value, length) \
    open_cfw_test_kvdb_setting_write((key), (value), (length))
#define OPEN_CFW_KVDB_SETTING_DIAGNOSTIC() \
    open_cfw_test_kvdb_setting_diagnostic()

#endif
