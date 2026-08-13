#ifndef OPEN_CFW_KVDB_ONBOARDING_CONFIG_HOST_H
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_HOST_H

extern unsigned char open_cfw_test_kvdb_onboarding_config_record[1];
extern unsigned char open_cfw_test_kvdb_onboarding_config_read_value[1];
extern unsigned char open_cfw_test_kvdb_onboarding_config_written[1];
extern unsigned int open_cfw_test_kvdb_onboarding_config_read_count;
extern unsigned int open_cfw_test_kvdb_onboarding_config_write_count;
extern unsigned int open_cfw_test_kvdb_onboarding_config_unknown_count;
extern unsigned int open_cfw_test_kvdb_onboarding_config_write_failure_count;
extern unsigned int open_cfw_test_kvdb_onboarding_config_read_failure_count;
extern int open_cfw_test_kvdb_onboarding_config_read_result;
extern int open_cfw_test_kvdb_onboarding_config_write_result;

void open_cfw_test_kvdb_onboarding_config_reset(void);
int open_cfw_test_kvdb_onboarding_config_read(
    const char *key, void *value, unsigned short length
);
int open_cfw_test_kvdb_onboarding_config_write(
    const char *key, const void *value, unsigned short length
);
void open_cfw_test_kvdb_onboarding_config_unknown(void);
void open_cfw_test_kvdb_onboarding_config_write_failure(void);
void open_cfw_test_kvdb_onboarding_config_read_failure(void);

#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_RECORD_ADDRESS \
    ((unsigned long)open_cfw_test_kvdb_onboarding_config_record)
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_READ(key, value, length) \
    open_cfw_test_kvdb_onboarding_config_read((key), (value), (length))
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_WRITE(key, value, length) \
    open_cfw_test_kvdb_onboarding_config_write((key), (value), (length))
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_UNKNOWN_INDEX() \
    open_cfw_test_kvdb_onboarding_config_unknown()
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_WRITE_FAILURE() \
    open_cfw_test_kvdb_onboarding_config_write_failure()
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_READ_FAILURE() \
    open_cfw_test_kvdb_onboarding_config_read_failure()

#endif
