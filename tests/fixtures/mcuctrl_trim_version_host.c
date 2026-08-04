#include <stddef.h>

unsigned int open_cfw_test_mcuctrl_trim_read_value;
unsigned int open_cfw_test_mcuctrl_trim_read_status;
unsigned int open_cfw_test_mcuctrl_trim_read_calls;
unsigned int open_cfw_test_mcuctrl_trim_info_space;
unsigned int open_cfw_test_mcuctrl_trim_word_offset;
unsigned int open_cfw_test_mcuctrl_trim_word_count;
unsigned int open_cfw_test_mcuctrl_trim_destination_nonnull;
unsigned int open_cfw_test_mcuctrl_trim_chiprev_values[4];
unsigned int open_cfw_test_mcuctrl_trim_chiprev_reads;
unsigned int open_cfw_test_mcuctrl_trim_chiprev_addresses[4];

static unsigned int open_cfw_test_mcuctrl_trim_info1_read(
    unsigned int info_space,
    unsigned int word_offset,
    unsigned int word_count,
    unsigned int *destination
)
{
    ++open_cfw_test_mcuctrl_trim_read_calls;
    open_cfw_test_mcuctrl_trim_info_space = info_space;
    open_cfw_test_mcuctrl_trim_word_offset = word_offset;
    open_cfw_test_mcuctrl_trim_word_count = word_count;
    open_cfw_test_mcuctrl_trim_destination_nonnull =
        destination != (unsigned int *)0;
    *destination = open_cfw_test_mcuctrl_trim_read_value;
    return open_cfw_test_mcuctrl_trim_read_status;
}

static unsigned int
open_cfw_test_mcuctrl_trim_read32(unsigned int address)
{
    unsigned int index = open_cfw_test_mcuctrl_trim_chiprev_reads;

    if (index > 3U) {
        index = 3U;
    }
    open_cfw_test_mcuctrl_trim_chiprev_addresses[index] = address;
    ++open_cfw_test_mcuctrl_trim_chiprev_reads;
    return open_cfw_test_mcuctrl_trim_chiprev_values[index];
}

void open_cfw_test_mcuctrl_trim_reset(void)
{
    unsigned int index;

    open_cfw_test_mcuctrl_trim_read_value = 0U;
    open_cfw_test_mcuctrl_trim_read_status = 0U;
    open_cfw_test_mcuctrl_trim_read_calls = 0U;
    open_cfw_test_mcuctrl_trim_info_space = 0U;
    open_cfw_test_mcuctrl_trim_word_offset = 0U;
    open_cfw_test_mcuctrl_trim_word_count = 0U;
    open_cfw_test_mcuctrl_trim_destination_nonnull = 0U;
    open_cfw_test_mcuctrl_trim_chiprev_reads = 0U;
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_mcuctrl_trim_chiprev_values[index] = 0U;
        open_cfw_test_mcuctrl_trim_chiprev_addresses[index] = 0U;
    }
}

#define OPEN_CFW_MCUCTRL_TRIM_INFO1_READ( \
    info_space, word_offset, word_count, destination \
) \
    open_cfw_test_mcuctrl_trim_info1_read( \
        (info_space), \
        (word_offset), \
        (word_count), \
        (destination) \
    )
#define OPEN_CFW_MCUCTRL_TRIM_READ32(address) \
    open_cfw_test_mcuctrl_trim_read32(address)

#include "../../components/apollo_main/core_overlay/mcuctrl_trim_version.c"
