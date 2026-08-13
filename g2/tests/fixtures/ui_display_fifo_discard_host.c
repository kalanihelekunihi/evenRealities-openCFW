unsigned int open_cfw_test_fifo_discard_read_calls;
unsigned int open_cfw_test_fifo_discard_read_result;
void *open_cfw_test_fifo_discard_read_handle;
void *open_cfw_test_fifo_discard_read_destination;
unsigned int open_cfw_test_fifo_discard_read_count;
unsigned int *open_cfw_test_fifo_discard_read_count_pointer;

void open_cfw_test_fifo_discard_reset(void)
{
    open_cfw_test_fifo_discard_read_calls = 0U;
    open_cfw_test_fifo_discard_read_result = 0U;
    open_cfw_test_fifo_discard_read_handle = (void *)0;
    open_cfw_test_fifo_discard_read_destination = (void *)1;
    open_cfw_test_fifo_discard_read_count = 0U;
    open_cfw_test_fifo_discard_read_count_pointer = (unsigned int *)1;
}

unsigned int open_cfw_test_fifo_discard_read(
    void *handle,
    void *destination,
    unsigned int count,
    unsigned int *read_count
)
{
    ++open_cfw_test_fifo_discard_read_calls;
    open_cfw_test_fifo_discard_read_handle = handle;
    open_cfw_test_fifo_discard_read_destination = destination;
    open_cfw_test_fifo_discard_read_count = count;
    open_cfw_test_fifo_discard_read_count_pointer = read_count;
    return open_cfw_test_fifo_discard_read_result;
}

#define OPEN_CFW_UI_DISPLAY_FIFO_DISCARD_READ( \
    handle, \
    destination, \
    count, \
    read_count \
) \
    open_cfw_test_fifo_discard_read( \
        (handle), \
        (destination), \
        (count), \
        (read_count) \
    )

#include "../../components/apollo_main/core_overlay/ui_display_fifo_discard.c"
