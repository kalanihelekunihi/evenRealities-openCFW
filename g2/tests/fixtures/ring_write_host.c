struct open_cfw_test_ring {
    unsigned int write_index;
    unsigned int read_index;
    unsigned int available;
    unsigned int capacity;
    unsigned int element_size;
    unsigned char *buffer;
};

unsigned int open_cfw_test_ring_write_interrupt_mask;
unsigned int open_cfw_test_ring_write_enter_count;
unsigned int open_cfw_test_ring_write_exit_count;
unsigned int open_cfw_test_ring_write_exit_mask;

unsigned int open_cfw_test_ring_write_critical_enter(void)
{
    ++open_cfw_test_ring_write_enter_count;
    return open_cfw_test_ring_write_interrupt_mask;
}

void open_cfw_test_ring_write_critical_exit(unsigned int interrupt_mask)
{
    ++open_cfw_test_ring_write_exit_count;
    open_cfw_test_ring_write_exit_mask = interrupt_mask;
}

void open_cfw_test_ring_write_reset(void)
{
    open_cfw_test_ring_write_interrupt_mask = 0U;
    open_cfw_test_ring_write_enter_count = 0U;
    open_cfw_test_ring_write_exit_count = 0U;
    open_cfw_test_ring_write_exit_mask = 0xFFFFFFFFU;
}

#define OPEN_CFW_RING_WRITE_CRITICAL_ENTER() \
    open_cfw_test_ring_write_critical_enter()
#define OPEN_CFW_RING_WRITE_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_test_ring_write_critical_exit(interrupt_mask)
#define OPEN_CFW_RING_WRITE_INDEX(ring) \
    (((struct open_cfw_test_ring *)(ring))->write_index)
#define OPEN_CFW_RING_WRITE_AVAILABLE(ring) \
    (((struct open_cfw_test_ring *)(ring))->available)
#define OPEN_CFW_RING_WRITE_CAPACITY(ring) \
    (((const struct open_cfw_test_ring *)(ring))->capacity)
#define OPEN_CFW_RING_WRITE_ELEMENT_SIZE(ring) \
    (((const struct open_cfw_test_ring *)(ring))->element_size)
#define OPEN_CFW_RING_WRITE_BUFFER(ring) \
    (((struct open_cfw_test_ring *)(ring))->buffer)

#include "../../components/apollo_main/core_overlay/ring_write.c"
