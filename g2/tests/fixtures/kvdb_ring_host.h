#ifndef OPEN_CFW_KVDB_RING_HOST_H
#define OPEN_CFW_KVDB_RING_HOST_H

extern unsigned char open_cfw_test_kvdb_ring_record[24];
extern unsigned char open_cfw_test_kvdb_ring_read_value[24];
extern unsigned char open_cfw_test_kvdb_ring_written[24];
extern unsigned int open_cfw_test_kvdb_ring_write_count;
extern unsigned int open_cfw_test_kvdb_ring_diagnostic_count;
extern int open_cfw_test_kvdb_ring_read_result;

void open_cfw_test_kvdb_ring_reset(void);
void open_cfw_test_kvdb_ring_set_read(const unsigned char *value, int result);
unsigned short open_cfw_test_kvdb_ring_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
);
int open_cfw_test_kvdb_ring_read(
    const char *key, void *value, unsigned short length
);
int open_cfw_test_kvdb_ring_write(
    const char *key, const void *value, unsigned short length
);
void open_cfw_test_kvdb_ring_diagnostic(void);

#define OPEN_CFW_KVDB_RING_RECORD_ADDRESS \
    ((unsigned long)open_cfw_test_kvdb_ring_record)
#define OPEN_CFW_KVDB_RING_CRC16(data, length, seed) \
    open_cfw_test_kvdb_ring_crc16((data), (length), (seed))
#define OPEN_CFW_KVDB_RING_READ(key, value, length) \
    open_cfw_test_kvdb_ring_read((key), (value), (length))
#define OPEN_CFW_KVDB_RING_WRITE(key, value, length) \
    open_cfw_test_kvdb_ring_write((key), (value), (length))
#define OPEN_CFW_KVDB_RING_DIAGNOSTIC() open_cfw_test_kvdb_ring_diagnostic()

#endif
