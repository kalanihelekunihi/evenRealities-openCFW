#include <stddef.h>

unsigned int open_cfw_test_mcuctrl_extclk32m_status_reads[4];
unsigned int open_cfw_test_mcuctrl_extclk32m_status_read_count;
unsigned int open_cfw_test_mcuctrl_extclk32m_status_addresses[4];

static unsigned int
open_cfw_test_mcuctrl_extclk32m_status_read32(unsigned int address)
{
    unsigned int index =
        open_cfw_test_mcuctrl_extclk32m_status_read_count;

    if (index > 3U) {
        index = 3U;
    }
    open_cfw_test_mcuctrl_extclk32m_status_addresses[index] = address;
    open_cfw_test_mcuctrl_extclk32m_status_read_count++;
    return open_cfw_test_mcuctrl_extclk32m_status_reads[index];
}

void open_cfw_test_mcuctrl_extclk32m_status_reset(void)
{
    unsigned int index;

    open_cfw_test_mcuctrl_extclk32m_status_read_count = 0U;
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_mcuctrl_extclk32m_status_reads[index] = 0U;
        open_cfw_test_mcuctrl_extclk32m_status_addresses[index] = 0U;
    }
}

#define OPEN_CFW_MCUCTRL_EXTCLK32M_STATUS_READ32(address) \
    open_cfw_test_mcuctrl_extclk32m_status_read32(address)

#include "../../components/apollo_main/core_overlay/mcuctrl_extclk32m_status.c"
