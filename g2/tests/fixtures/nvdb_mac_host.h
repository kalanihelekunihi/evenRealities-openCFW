#ifndef OPEN_CFW_TEST_NVDB_MAC_HOST_H
#define OPEN_CFW_TEST_NVDB_MAC_HOST_H

extern unsigned char open_cfw_test_nvdb_mac_record[10];

void open_cfw_test_nvdb_mac_device_ids_get(
    unsigned int *chip_id0,
    unsigned int *chip_id1
);
unsigned int open_cfw_test_nvdb_mac_crc32(
    const unsigned char *data,
    unsigned int length,
    const unsigned int *seed
);
unsigned short open_cfw_test_nvdb_mac_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
);
int open_cfw_test_nvdb_mac_read(
    const char *key,
    void *value,
    unsigned short length
);
int open_cfw_test_nvdb_mac_write(
    const char *key,
    const void *value,
    unsigned short length
);
void open_cfw_test_nvdb_mac_diagnostic(void);
void open_cfw_test_nvdb_mac_reset(void);
void open_cfw_test_nvdb_mac_set_device_ids(
    unsigned int chip_id0,
    unsigned int chip_id1
);
void open_cfw_test_nvdb_mac_set_read_record(
    const unsigned char *value,
    int result
);

#define OPEN_CFW_NVDB_MAC_RECORD_ADDRESS \
    ((unsigned long)&open_cfw_test_nvdb_mac_record[0])
#define OPEN_CFW_NVDB_MAC_KEY "nvMAC"
#define OPEN_CFW_NVDB_MAC_DEVICE_IDS_GET(chip_id0, chip_id1) \
    open_cfw_test_nvdb_mac_device_ids_get((chip_id0), (chip_id1))
#define OPEN_CFW_NVDB_MAC_CRC32(data, length, seed) \
    open_cfw_test_nvdb_mac_crc32((data), (length), (seed))
#define OPEN_CFW_NVDB_MAC_CRC16(data, length, seed) \
    open_cfw_test_nvdb_mac_crc16((data), (length), (seed))
#define OPEN_CFW_NVDB_MAC_READ(key, value, length) \
    open_cfw_test_nvdb_mac_read((key), (value), (length))
#define OPEN_CFW_NVDB_MAC_WRITE(key, value, length) \
    open_cfw_test_nvdb_mac_write((key), (value), (length))
#define OPEN_CFW_NVDB_MAC_DIAGNOSTIC() \
    open_cfw_test_nvdb_mac_diagnostic()

#endif
