#ifndef OPEN_CFW_TEST_NVDB_SENSOR_CALDATA_HOST_H
#define OPEN_CFW_TEST_NVDB_SENSOR_CALDATA_HOST_H

extern unsigned char open_cfw_test_nvdb_sensor_caldata_record[92];
extern unsigned char open_cfw_test_nvdb_sensor_caldata_ag_record[68];

unsigned short open_cfw_test_nvdb_sensor_caldata_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
);
int open_cfw_test_nvdb_sensor_caldata_read(
    const char *key,
    void *value,
    unsigned short length
);
int open_cfw_test_nvdb_sensor_caldata_write(
    const char *key,
    const void *value,
    unsigned short length
);
int open_cfw_test_nvdb_sensor_caldata_pattern_check_enabled(void);
void open_cfw_test_nvdb_sensor_caldata_diagnostic(void);
void open_cfw_test_nvdb_sensor_caldata_reset(void);
void open_cfw_test_nvdb_sensor_caldata_set_read(
    const char *key,
    const unsigned char *value,
    int result
);
void open_cfw_test_nvdb_sensor_caldata_set_pattern_check(int enabled);

#define OPEN_CFW_NVDB_SENSOR_CALDATA_RECORD_ADDRESS \
    ((unsigned long)&open_cfw_test_nvdb_sensor_caldata_record[0])
#define OPEN_CFW_NVDB_SENSOR_CALDATA_AG_RECORD_ADDRESS \
    ((unsigned long)&open_cfw_test_nvdb_sensor_caldata_ag_record[0])
#define OPEN_CFW_NVDB_SENSOR_CALDATA_KEY "nvSCald"
#define OPEN_CFW_NVDB_SENSOR_CALDATA_AG_KEY "nvSCaldAG"
#define OPEN_CFW_NVDB_SENSOR_CALDATA_CRC16(data, length, seed) \
    open_cfw_test_nvdb_sensor_caldata_crc16((data), (length), (seed))
#define OPEN_CFW_NVDB_SENSOR_CALDATA_READ(key, value, length) \
    open_cfw_test_nvdb_sensor_caldata_read((key), (value), (length))
#define OPEN_CFW_NVDB_SENSOR_CALDATA_WRITE(key, value, length) \
    open_cfw_test_nvdb_sensor_caldata_write((key), (value), (length))
#define OPEN_CFW_NVDB_SENSOR_CALDATA_PATTERN_CHECK_ENABLED() \
    open_cfw_test_nvdb_sensor_caldata_pattern_check_enabled()
#define OPEN_CFW_NVDB_SENSOR_CALDATA_DIAGNOSTIC() \
    open_cfw_test_nvdb_sensor_caldata_diagnostic()

#endif
