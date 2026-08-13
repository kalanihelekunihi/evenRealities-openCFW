#include <string.h>

#include "kvdb_onboarding_config_host.h"

unsigned char open_cfw_test_kvdb_onboarding_config_record[1];
unsigned char open_cfw_test_kvdb_onboarding_config_read_value[1];
unsigned char open_cfw_test_kvdb_onboarding_config_written[1];
unsigned int open_cfw_test_kvdb_onboarding_config_read_count;
unsigned int open_cfw_test_kvdb_onboarding_config_write_count;
unsigned int open_cfw_test_kvdb_onboarding_config_unknown_count;
unsigned int open_cfw_test_kvdb_onboarding_config_write_failure_count;
unsigned int open_cfw_test_kvdb_onboarding_config_read_failure_count;
int open_cfw_test_kvdb_onboarding_config_read_result;
int open_cfw_test_kvdb_onboarding_config_write_result;

int open_cfw_test_kvdb_onboarding_config_read(
    const char *key, void *value, unsigned short length
)
{
    if (strcmp(key, "kvOnboardingConfig") != 0 || length != 1u) {
        return -9;
    }
    memcpy(value, open_cfw_test_kvdb_onboarding_config_read_value, 1u);
    ++open_cfw_test_kvdb_onboarding_config_read_count;
    return open_cfw_test_kvdb_onboarding_config_read_result;
}

int open_cfw_test_kvdb_onboarding_config_write(
    const char *key, const void *value, unsigned short length
)
{
    if (strcmp(key, "kvOnboardingConfig") != 0 || length != 1u) {
        return -9;
    }
    memcpy(open_cfw_test_kvdb_onboarding_config_written, value, 1u);
    ++open_cfw_test_kvdb_onboarding_config_write_count;
    return open_cfw_test_kvdb_onboarding_config_write_result;
}

void open_cfw_test_kvdb_onboarding_config_unknown(void)
{
    ++open_cfw_test_kvdb_onboarding_config_unknown_count;
}

void open_cfw_test_kvdb_onboarding_config_write_failure(void)
{
    ++open_cfw_test_kvdb_onboarding_config_write_failure_count;
}

void open_cfw_test_kvdb_onboarding_config_read_failure(void)
{
    ++open_cfw_test_kvdb_onboarding_config_read_failure_count;
}

void open_cfw_test_kvdb_onboarding_config_reset(void)
{
    open_cfw_test_kvdb_onboarding_config_record[0] = 0;
    open_cfw_test_kvdb_onboarding_config_read_value[0] = 0;
    open_cfw_test_kvdb_onboarding_config_written[0] = 0;
    open_cfw_test_kvdb_onboarding_config_read_count = 0;
    open_cfw_test_kvdb_onboarding_config_write_count = 0;
    open_cfw_test_kvdb_onboarding_config_unknown_count = 0;
    open_cfw_test_kvdb_onboarding_config_write_failure_count = 0;
    open_cfw_test_kvdb_onboarding_config_read_failure_count = 0;
    open_cfw_test_kvdb_onboarding_config_read_result = 1;
    open_cfw_test_kvdb_onboarding_config_write_result = 0;
}
