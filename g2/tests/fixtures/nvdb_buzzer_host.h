#ifndef OPEN_CFW_TEST_NVDB_BUZZER_HOST_H
#define OPEN_CFW_TEST_NVDB_BUZZER_HOST_H

extern unsigned char open_cfw_test_nvdb_buzzer_record[12];

unsigned short open_cfw_test_nvdb_buzzer_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
);
int open_cfw_test_nvdb_buzzer_read(
    const char *key,
    void *value,
    unsigned short length
);
int open_cfw_test_nvdb_buzzer_write(
    const char *key,
    const void *value,
    unsigned short length
);
void open_cfw_test_nvdb_buzzer_diagnostic(void);
void open_cfw_test_nvdb_buzzer_reset(void);
void open_cfw_test_nvdb_buzzer_set_read_record(
    const unsigned char *value,
    int result
);

#define OPEN_CFW_NVDB_BUZZER_RECORD_ADDRESS \
    ((unsigned long)&open_cfw_test_nvdb_buzzer_record[0])
#define OPEN_CFW_NVDB_BUZZER_KEY "nvBuzzer"
#define OPEN_CFW_NVDB_BUZZER_CRC16(data, length, seed) \
    open_cfw_test_nvdb_buzzer_crc16((data), (length), (seed))
#define OPEN_CFW_NVDB_BUZZER_READ(key, value, length) \
    open_cfw_test_nvdb_buzzer_read((key), (value), (length))
#define OPEN_CFW_NVDB_BUZZER_WRITE(key, value, length) \
    open_cfw_test_nvdb_buzzer_write((key), (value), (length))
#define OPEN_CFW_NVDB_BUZZER_DIAGNOSTIC() \
    open_cfw_test_nvdb_buzzer_diagnostic()

#endif
