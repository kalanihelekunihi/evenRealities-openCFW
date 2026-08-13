#include <stdint.h>

unsigned int open_cfw_test_info1_registers[32];
unsigned int open_cfw_test_info1_shadow_valid;
unsigned int open_cfw_test_info1_power_status;
unsigned int open_cfw_test_info1_shadow_reads;
unsigned int open_cfw_test_info1_power_reads;
unsigned int open_cfw_test_info1_call_count;
unsigned int open_cfw_test_info1_fail_call;
unsigned int open_cfw_test_info1_fail_status;
unsigned int open_cfw_test_info1_call_info_space[9];
unsigned int open_cfw_test_info1_call_word_offset[9];
unsigned int open_cfw_test_info1_call_word_count[9];

static unsigned int
open_cfw_test_info1_read_register(unsigned int address)
{
    if (address == 0x400201BCU) {
        ++open_cfw_test_info1_shadow_reads;
        return open_cfw_test_info1_shadow_valid;
    }
    if (address == 0x40021008U) {
        ++open_cfw_test_info1_power_reads;
        return open_cfw_test_info1_power_status;
    }
    return 0U;
}

static unsigned int open_cfw_test_info1_read(
    unsigned int info_space,
    unsigned int word_offset,
    unsigned int word_count,
    unsigned int *destination
)
{
    unsigned int call = open_cfw_test_info1_call_count;
    unsigned int index;

    open_cfw_test_info1_call_info_space[call] = info_space;
    open_cfw_test_info1_call_word_offset[call] = word_offset;
    open_cfw_test_info1_call_word_count[call] = word_count;
    ++open_cfw_test_info1_call_count;

    if (call == open_cfw_test_info1_fail_call) {
        return open_cfw_test_info1_fail_status;
    }

    for (index = 0U; index < word_count; ++index) {
        destination[index] =
            0xA0000000U | (call << 16) | index;
    }
    return 0U;
}

#define OPEN_CFW_PWRCTRL_INFO1_REGS_ADDRESS \
    ((__UINTPTR_TYPE__)open_cfw_test_info1_registers)
#define OPEN_CFW_PWRCTRL_INFO1_READ_REGISTER(address) \
    open_cfw_test_info1_read_register(address)
#define OPEN_CFW_PWRCTRL_INFO1_READ( \
    info_space, word_offset, word_count, destination \
) \
    open_cfw_test_info1_read( \
        (info_space), \
        (word_offset), \
        (word_count), \
        (destination) \
    )

#include "../../components/apollo_main/core_overlay/pwrctrl_info1_populate.c"

void open_cfw_test_info1_reset(void)
{
    unsigned int index;

    for (index = 0U; index < 32U; ++index) {
        open_cfw_test_info1_registers[index] =
            0xCC000000U | index;
    }
    for (index = 0U; index < 9U; ++index) {
        open_cfw_test_info1_call_info_space[index] = 0U;
        open_cfw_test_info1_call_word_offset[index] = 0U;
        open_cfw_test_info1_call_word_count[index] = 0U;
    }
    open_cfw_test_info1_shadow_valid = 1U << 3;
    open_cfw_test_info1_power_status = 1U << 27;
    open_cfw_test_info1_shadow_reads = 0U;
    open_cfw_test_info1_power_reads = 0U;
    open_cfw_test_info1_call_count = 0U;
    open_cfw_test_info1_fail_call = 0xFFFFFFFFU;
    open_cfw_test_info1_fail_status = 0x55U;
}
