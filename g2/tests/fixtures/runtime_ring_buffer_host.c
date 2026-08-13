#include <stdint.h>

static uint32_t open_cfw_test_ring_buffer_assert_count;

static void open_cfw_test_ring_buffer_assert_power_of_two(void)
{
    open_cfw_test_ring_buffer_assert_count += 1U;
}

#define OPEN_CFW_RING_BUFFER_HOST_TEST 1
#define OPEN_CFW_RING_BUFFER_ASSERT_POWER_OF_TWO() \
    open_cfw_test_ring_buffer_assert_power_of_two()
#include "../../components/shared/ring_buffer/runtime_ring_buffer.c"

uint32_t open_cfw_test_ring_buffer_get_assert_count(void)
{
    return open_cfw_test_ring_buffer_assert_count;
}

void open_cfw_test_ring_buffer_reset_assert_count(void)
{
    open_cfw_test_ring_buffer_assert_count = 0U;
}
