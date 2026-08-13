#ifndef OPEN_CFW_KVDB_TERMINAL_MODE_HOST_H
#define OPEN_CFW_KVDB_TERMINAL_MODE_HOST_H

extern unsigned char open_cfw_test_kvdb_terminal_mode_record[4];
extern unsigned char open_cfw_test_kvdb_terminal_mode_read_value[4];
extern unsigned char open_cfw_test_kvdb_terminal_mode_written[4];
extern unsigned int open_cfw_test_kvdb_terminal_mode_write_count;
extern unsigned int open_cfw_test_kvdb_terminal_mode_diagnostic_count;
extern int open_cfw_test_kvdb_terminal_mode_read_result;

void open_cfw_test_kvdb_terminal_mode_reset(void);
void open_cfw_test_kvdb_terminal_mode_set_read(
    const unsigned char *value, int result
);
unsigned short open_cfw_test_kvdb_terminal_mode_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
);
int open_cfw_test_kvdb_terminal_mode_read(
    const char *key, void *value, unsigned short length
);
int open_cfw_test_kvdb_terminal_mode_write(
    const char *key, const void *value, unsigned short length
);
void open_cfw_test_kvdb_terminal_mode_diagnostic(void);

#define OPEN_CFW_KVDB_TERMINAL_MODE_RECORD_ADDRESS \
    ((unsigned long)open_cfw_test_kvdb_terminal_mode_record)
#define OPEN_CFW_KVDB_TERMINAL_MODE_CRC16(data, length, seed) \
    open_cfw_test_kvdb_terminal_mode_crc16((data), (length), (seed))
#define OPEN_CFW_KVDB_TERMINAL_MODE_READ(key, value, length) \
    open_cfw_test_kvdb_terminal_mode_read((key), (value), (length))
#define OPEN_CFW_KVDB_TERMINAL_MODE_WRITE(key, value, length) \
    open_cfw_test_kvdb_terminal_mode_write((key), (value), (length))
#define OPEN_CFW_KVDB_TERMINAL_MODE_DIAGNOSTIC() \
    open_cfw_test_kvdb_terminal_mode_diagnostic()

#endif
