#include <stdint.h>

unsigned int open_cfw_test_pwrctrl_trim_cache;
unsigned int open_cfw_test_pwrctrl_trim_read_value;
unsigned int open_cfw_test_pwrctrl_trim_read_status;
unsigned int open_cfw_test_pwrctrl_trim_read_calls;
unsigned int open_cfw_test_pwrctrl_trim_info_space;
unsigned int open_cfw_test_pwrctrl_trim_word_offset;
unsigned int open_cfw_test_pwrctrl_trim_word_count;
unsigned int open_cfw_test_pwrctrl_trim_destination_matches_cache;

void open_cfw_test_pwrctrl_trim_reset(void)
{
    open_cfw_test_pwrctrl_trim_cache = 0xFFFFFFFFU;
    open_cfw_test_pwrctrl_trim_read_value = 1U;
    open_cfw_test_pwrctrl_trim_read_status = 0U;
    open_cfw_test_pwrctrl_trim_read_calls = 0U;
    open_cfw_test_pwrctrl_trim_info_space = 0U;
    open_cfw_test_pwrctrl_trim_word_offset = 0U;
    open_cfw_test_pwrctrl_trim_word_count = 0U;
    open_cfw_test_pwrctrl_trim_destination_matches_cache = 0U;
}

unsigned int open_cfw_test_pwrctrl_trim_info1_read(
    unsigned int info_space,
    unsigned int word_offset,
    unsigned int word_count,
    unsigned int *destination
)
{
    ++open_cfw_test_pwrctrl_trim_read_calls;
    open_cfw_test_pwrctrl_trim_info_space = info_space;
    open_cfw_test_pwrctrl_trim_word_offset = word_offset;
    open_cfw_test_pwrctrl_trim_word_count = word_count;
    open_cfw_test_pwrctrl_trim_destination_matches_cache =
        destination == &open_cfw_test_pwrctrl_trim_cache;
    *destination = open_cfw_test_pwrctrl_trim_read_value;
    return open_cfw_test_pwrctrl_trim_read_status;
}

#define OPEN_CFW_PWRCTRL_TRIM_CACHE_ADDRESS \
    ((__UINTPTR_TYPE__)&open_cfw_test_pwrctrl_trim_cache)
#define OPEN_CFW_PWRCTRL_TRIM_INFO1_READ( \
    info_space, word_offset, word_count, destination \
) \
    open_cfw_test_pwrctrl_trim_info1_read( \
        (info_space), \
        (word_offset), \
        (word_count), \
        (destination) \
    )

#include "../../components/apollo_main/core_overlay/pwrctrl_trim_version.c"
