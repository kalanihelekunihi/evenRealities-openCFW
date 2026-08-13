#ifndef OPEN_CFW_TEST_NVDB_SYS_DT_HOST_H
#define OPEN_CFW_TEST_NVDB_SYS_DT_HOST_H

extern unsigned char open_cfw_test_nvdb_sys_dt_record[172];
extern unsigned char open_cfw_test_nvdb_sys_dt_otp_psn[15];
extern unsigned char open_cfw_test_nvdb_sys_dt_month_buffer[4];
extern unsigned char open_cfw_test_nvdb_sys_dt_legacy_psn_flag;

unsigned short open_cfw_test_nvdb_sys_dt_crc16(
    const unsigned char *data,
    unsigned int length,
    const unsigned short *seed
);
int open_cfw_test_nvdb_sys_dt_read(
    const char *key,
    void *value,
    unsigned short length
);
int open_cfw_test_nvdb_sys_dt_write(
    const char *key,
    const void *value,
    unsigned short length
);
void open_cfw_test_nvdb_sys_dt_otp_begin(void);
void open_cfw_test_nvdb_sys_dt_otp_end(void);
int open_cfw_test_nvdb_sys_dt_otp_read_word(
    unsigned int offset,
    unsigned int *value
);
int open_cfw_test_nvdb_sys_dt_otp_write_word(
    unsigned int offset,
    unsigned int value
);
void open_cfw_test_nvdb_sys_dt_parsed(
    const char *project_code,
    char manufacturer_code,
    const char *manufacturer,
    char color,
    char year_code,
    unsigned int year,
    char month_code,
    const char *month,
    const char *day,
    const char *serial_number
);
void open_cfw_test_nvdb_sys_dt_diagnostic(void);

void open_cfw_test_nvdb_sys_dt_reset(void);
void open_cfw_test_nvdb_sys_dt_set_read(
    const unsigned char *value,
    int result
);
void open_cfw_test_nvdb_sys_dt_set_otp_slot(
    unsigned int slot,
    const unsigned char *value
);
void open_cfw_test_nvdb_sys_dt_set_otp_read_failure(
    unsigned int slot,
    unsigned int word,
    int status
);
void open_cfw_test_nvdb_sys_dt_set_otp_write_failure(
    unsigned int word,
    int status
);

#define OPEN_CFW_NVDB_SYS_DT_RECORD_ADDRESS \
    ((unsigned long)&open_cfw_test_nvdb_sys_dt_record[0])
#define OPEN_CFW_NVDB_SYS_DT_OTP_PSN_ADDRESS \
    ((unsigned long)&open_cfw_test_nvdb_sys_dt_otp_psn[0])
#define OPEN_CFW_NVDB_SYS_DT_MONTH_BUFFER_ADDRESS \
    ((unsigned long)&open_cfw_test_nvdb_sys_dt_month_buffer[0])
#define OPEN_CFW_NVDB_SYS_DT_LEGACY_PSN_FLAG_ADDRESS \
    ((unsigned long)&open_cfw_test_nvdb_sys_dt_legacy_psn_flag)
#define OPEN_CFW_NVDB_SYS_DT_KEY "nvSysDt"
#define OPEN_CFW_NVDB_SYS_DT_CRC16(data, length, seed) \
    open_cfw_test_nvdb_sys_dt_crc16((data), (length), (seed))
#define OPEN_CFW_NVDB_SYS_DT_READ(key, value, length) \
    open_cfw_test_nvdb_sys_dt_read((key), (value), (length))
#define OPEN_CFW_NVDB_SYS_DT_WRITE(key, value, length) \
    open_cfw_test_nvdb_sys_dt_write((key), (value), (length))
#define OPEN_CFW_NVDB_SYS_DT_OTP_BEGIN() \
    open_cfw_test_nvdb_sys_dt_otp_begin()
#define OPEN_CFW_NVDB_SYS_DT_OTP_END() \
    open_cfw_test_nvdb_sys_dt_otp_end()
#define OPEN_CFW_NVDB_SYS_DT_OTP_READ_WORD(offset, value) \
    open_cfw_test_nvdb_sys_dt_otp_read_word((offset), (value))
#define OPEN_CFW_NVDB_SYS_DT_OTP_WRITE_WORD(offset, value) \
    open_cfw_test_nvdb_sys_dt_otp_write_word((offset), (value))
#define OPEN_CFW_NVDB_SYS_DT_PARSED(...) \
    open_cfw_test_nvdb_sys_dt_parsed(__VA_ARGS__)
#define OPEN_CFW_NVDB_SYS_DT_DIAGNOSTIC() \
    open_cfw_test_nvdb_sys_dt_diagnostic()

#endif
