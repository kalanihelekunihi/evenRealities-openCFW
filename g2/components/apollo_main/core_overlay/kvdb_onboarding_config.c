/* Clean-room reconstruction of service_kvdb_onboarding_config.c. */

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_KVDB_ONBOARDING_CONFIG_RECORD_ADDRESS
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_RECORD_ADDRESS 0x20000040u
#endif
#ifndef OPEN_CFW_KVDB_ONBOARDING_CONFIG_KEY
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_KEY "kvOnboardingConfig"
#endif
#ifndef OPEN_CFW_KVDB_ONBOARDING_CONFIG_READ
int open_cfw_kvdb_onboarding_config_db_read(
    const char *key, void *value, uint16_t length
);
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_READ(key, value, length) \
    open_cfw_kvdb_onboarding_config_db_read((key), (value), (length))
#endif
#ifndef OPEN_CFW_KVDB_ONBOARDING_CONFIG_WRITE
int open_cfw_kvdb_onboarding_config_db_write(
    const char *key, const void *value, uint16_t length
);
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_WRITE(key, value, length) \
    open_cfw_kvdb_onboarding_config_db_write((key), (value), (length))
#endif
#ifndef OPEN_CFW_KVDB_ONBOARDING_CONFIG_UNKNOWN_INDEX
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_UNKNOWN_INDEX() ((void)0)
#endif
#ifndef OPEN_CFW_KVDB_ONBOARDING_CONFIG_WRITE_FAILURE
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_WRITE_FAILURE() ((void)0)
#endif
#ifndef OPEN_CFW_KVDB_ONBOARDING_CONFIG_READ_FAILURE
#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_READ_FAILURE() ((void)0)
#endif

#define OPEN_CFW_KVDB_ONBOARDING_CONFIG_RECORD \
    ((volatile uint8_t *)(uintptr_t) \
        OPEN_CFW_KVDB_ONBOARDING_CONFIG_RECORD_ADDRESS)

int open_cfw_kvdb_onboarding_config_set_indexed(
    uint8_t data_index, const uint8_t *value
)
{
    if (data_index == 0u) {
        if (value != NULL) {
            *OPEN_CFW_KVDB_ONBOARDING_CONFIG_RECORD = *value;
        }
        return 0;
    }

    OPEN_CFW_KVDB_ONBOARDING_CONFIG_UNKNOWN_INDEX();
    return -1;
}

int open_cfw_kvdb_onboarding_config_persist(void)
{
    int result = OPEN_CFW_KVDB_ONBOARDING_CONFIG_WRITE(
        OPEN_CFW_KVDB_ONBOARDING_CONFIG_KEY,
        (const void *)(uintptr_t)OPEN_CFW_KVDB_ONBOARDING_CONFIG_RECORD,
        1u
    );

    if (result != 0) {
        OPEN_CFW_KVDB_ONBOARDING_CONFIG_WRITE_FAILURE();
    }
    return result;
}

int open_cfw_kvdb_onboarding_config_update_and_persist(
    uint8_t data_index, const uint8_t *value
)
{
    int result = open_cfw_kvdb_onboarding_config_set_indexed(
        data_index, value
    );

    if (result == 0) {
        result = open_cfw_kvdb_onboarding_config_persist();
    }
    return result;
}

uint8_t open_cfw_kvdb_onboarding_config_get(void)
{
    return *OPEN_CFW_KVDB_ONBOARDING_CONFIG_RECORD;
}

volatile uint8_t *open_cfw_kvdb_onboarding_config_pointer(uint8_t data_index)
{
    (void)data_index;
    return OPEN_CFW_KVDB_ONBOARDING_CONFIG_RECORD;
}

volatile uint8_t *open_cfw_kvdb_onboarding_config_read(uint8_t data_index)
{
    int result = OPEN_CFW_KVDB_ONBOARDING_CONFIG_READ(
        OPEN_CFW_KVDB_ONBOARDING_CONFIG_KEY,
        (void *)(uintptr_t)OPEN_CFW_KVDB_ONBOARDING_CONFIG_RECORD,
        1u
    );

    if (result == 0) {
        OPEN_CFW_KVDB_ONBOARDING_CONFIG_READ_FAILURE();
    }
    return open_cfw_kvdb_onboarding_config_pointer(data_index);
}
