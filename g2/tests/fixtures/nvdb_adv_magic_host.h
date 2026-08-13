#ifndef OPEN_CFW_TEST_NVDB_ADV_MAGIC_HOST_H
#define OPEN_CFW_TEST_NVDB_ADV_MAGIC_HOST_H

extern unsigned char open_cfw_test_nvdb_adv_magic_record[4];

unsigned short open_cfw_test_nvdb_adv_magic_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
);
int open_cfw_test_nvdb_adv_magic_read(
    const char *key,
    void *value,
    unsigned short length
);
int open_cfw_test_nvdb_adv_magic_write(
    const char *key,
    const void *value,
    unsigned short length
);
void open_cfw_test_nvdb_adv_magic_reset(void);
void open_cfw_test_nvdb_adv_magic_set_read_record(
    const unsigned char *value,
    int result
);

#define OPEN_CFW_NVDB_ADV_MAGIC_RECORD_ADDRESS \
    ((unsigned long)&open_cfw_test_nvdb_adv_magic_record[0])
#define OPEN_CFW_NVDB_ADV_MAGIC_KEY "nvAdvMagic"
#define OPEN_CFW_NVDB_ADV_MAGIC_CRC16(data, length, seed) \
    open_cfw_test_nvdb_adv_magic_crc16((data), (length), (seed))
#define OPEN_CFW_NVDB_ADV_MAGIC_READ(key, value, length) \
    open_cfw_test_nvdb_adv_magic_read((key), (value), (length))
#define OPEN_CFW_NVDB_ADV_MAGIC_WRITE(key, value, length) \
    open_cfw_test_nvdb_adv_magic_write((key), (value), (length))

#endif
