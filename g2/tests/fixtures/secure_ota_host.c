/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Native register/state/programmer fixture for the Apollo510 secure-OTA
 * addition routine.
 */

#define OPEN_CFW_TEST_SECURE_OTA_POINTER_REGISTER 0x40020264U

struct open_cfw_test_secure_ota_state_type {
    unsigned int mram_size;
    unsigned int descriptor_address;
    unsigned int image_count;
};

struct open_cfw_test_secure_ota_state_type
    open_cfw_test_secure_ota_state;
unsigned int open_cfw_test_secure_ota_pointer;
unsigned int open_cfw_test_secure_ota_program_result;
unsigned int open_cfw_test_secure_ota_program_calls;
unsigned int open_cfw_test_secure_ota_program_key;
unsigned int open_cfw_test_secure_ota_program_value;
unsigned int open_cfw_test_secure_ota_program_destination;
unsigned int open_cfw_test_secure_ota_program_count;
unsigned int open_cfw_test_secure_ota_read_calls;
unsigned int open_cfw_test_secure_ota_write_calls;
unsigned int open_cfw_test_secure_ota_write_address;
unsigned int open_cfw_test_secure_ota_write_value;

void open_cfw_test_secure_ota_reset(void)
{
    open_cfw_test_secure_ota_state.mram_size = 0x00400000U;
    open_cfw_test_secure_ota_state.descriptor_address = 0x007F0000U;
    open_cfw_test_secure_ota_state.image_count = 0U;
    open_cfw_test_secure_ota_pointer = 0U;
    open_cfw_test_secure_ota_program_result = 0U;
    open_cfw_test_secure_ota_program_calls = 0U;
    open_cfw_test_secure_ota_program_key = 0U;
    open_cfw_test_secure_ota_program_value = 0U;
    open_cfw_test_secure_ota_program_destination = 0U;
    open_cfw_test_secure_ota_program_count = 0U;
    open_cfw_test_secure_ota_read_calls = 0U;
    open_cfw_test_secure_ota_write_calls = 0U;
    open_cfw_test_secure_ota_write_address = 0U;
    open_cfw_test_secure_ota_write_value = 0U;
}

unsigned int open_cfw_test_secure_ota_read(unsigned int address)
{
    ++open_cfw_test_secure_ota_read_calls;
    if (address == OPEN_CFW_TEST_SECURE_OTA_POINTER_REGISTER) {
        return open_cfw_test_secure_ota_pointer;
    }
    return 0U;
}

void open_cfw_test_secure_ota_write(
    unsigned int address,
    unsigned int value
)
{
    ++open_cfw_test_secure_ota_write_calls;
    open_cfw_test_secure_ota_write_address = address;
    open_cfw_test_secure_ota_write_value = value;
    if (address == OPEN_CFW_TEST_SECURE_OTA_POINTER_REGISTER) {
        open_cfw_test_secure_ota_pointer = value;
    }
}

unsigned int open_cfw_test_secure_ota_program_words(
    unsigned int key,
    unsigned int *source,
    unsigned int *destination,
    unsigned int count
)
{
    ++open_cfw_test_secure_ota_program_calls;
    open_cfw_test_secure_ota_program_key = key;
    open_cfw_test_secure_ota_program_value = *source;
    open_cfw_test_secure_ota_program_destination =
        (unsigned int)(__UINTPTR_TYPE__)destination;
    open_cfw_test_secure_ota_program_count = count;
    return open_cfw_test_secure_ota_program_result;
}

#define OPEN_CFW_SECURE_OTA_STATE_ADDRESS \
    ((__UINTPTR_TYPE__)&open_cfw_test_secure_ota_state)
#define OPEN_CFW_SECURE_OTA_READ(address) \
    open_cfw_test_secure_ota_read(address)
#define OPEN_CFW_SECURE_OTA_WRITE(address, value) \
    open_cfw_test_secure_ota_write((address), (value))
#define OPEN_CFW_SECURE_OTA_PROGRAM_WORDS( \
    key, source, destination, count \
) \
    open_cfw_test_secure_ota_program_words( \
        (key), (source), (destination), (count) \
    )

#include "../../components/apollo_main/core_overlay/secure_ota.c"
