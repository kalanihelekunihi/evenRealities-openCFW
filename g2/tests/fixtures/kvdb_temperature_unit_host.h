#ifndef OPEN_CFW_KVDB_TEMPERATURE_UNIT_HOST_H
#define OPEN_CFW_KVDB_TEMPERATURE_UNIT_HOST_H

extern unsigned char open_cfw_test_kvdb_temperature_unit_record[12];
extern unsigned char open_cfw_test_kvdb_temperature_unit_read_value[12];
extern unsigned char open_cfw_test_kvdb_temperature_unit_written[12];
extern unsigned int open_cfw_test_kvdb_temperature_unit_write_count;
extern unsigned int open_cfw_test_kvdb_temperature_unit_diagnostic_count;
extern int open_cfw_test_kvdb_temperature_unit_read_result;

void open_cfw_test_kvdb_temperature_unit_reset(void);
void open_cfw_test_kvdb_temperature_unit_set_read(
    const unsigned char *value,
    int result
);

unsigned short open_cfw_test_kvdb_temperature_unit_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
);
int open_cfw_test_kvdb_temperature_unit_read(
    const char *key,
    void *value,
    unsigned short length
);
int open_cfw_test_kvdb_temperature_unit_write(
    const char *key,
    const void *value,
    unsigned short length
);
void open_cfw_test_kvdb_temperature_unit_diagnostic(void);

#define OPEN_CFW_KVDB_TEMPERATURE_UNIT_RECORD_ADDRESS \
    ((unsigned long)open_cfw_test_kvdb_temperature_unit_record)
#define OPEN_CFW_KVDB_TEMPERATURE_UNIT_CRC16(data, length, seed) \
    open_cfw_test_kvdb_temperature_unit_crc16((data), (length), (seed))
#define OPEN_CFW_KVDB_TEMPERATURE_UNIT_READ(key, value, length) \
    open_cfw_test_kvdb_temperature_unit_read((key), (value), (length))
#define OPEN_CFW_KVDB_TEMPERATURE_UNIT_WRITE(key, value, length) \
    open_cfw_test_kvdb_temperature_unit_write((key), (value), (length))
#define OPEN_CFW_KVDB_TEMPERATURE_UNIT_DIAGNOSTIC() \
    open_cfw_test_kvdb_temperature_unit_diagnostic()

#endif
