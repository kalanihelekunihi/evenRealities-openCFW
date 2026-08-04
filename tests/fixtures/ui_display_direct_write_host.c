unsigned int open_cfw_test_display_direct_instance;
unsigned int open_cfw_test_display_direct_full_after;
unsigned int open_cfw_test_display_direct_status_checks;
unsigned int open_cfw_test_display_direct_write_count;
unsigned int open_cfw_test_display_direct_written_values[16];
unsigned int open_cfw_test_display_direct_status_instances[16];
unsigned int open_cfw_test_display_direct_write_instances[16];

void open_cfw_test_display_direct_reset(void)
{
    unsigned int index;

    open_cfw_test_display_direct_instance = 3U;
    open_cfw_test_display_direct_full_after = 16U;
    open_cfw_test_display_direct_status_checks = 0U;
    open_cfw_test_display_direct_write_count = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_display_direct_written_values[index] = 0U;
        open_cfw_test_display_direct_status_instances[index] = 0U;
        open_cfw_test_display_direct_write_instances[index] = 0U;
    }
}

unsigned int open_cfw_test_display_direct_fifo_full(
    unsigned int instance
)
{
    unsigned int check = open_cfw_test_display_direct_status_checks;

    open_cfw_test_display_direct_status_instances[check] = instance;
    ++open_cfw_test_display_direct_status_checks;
    return open_cfw_test_display_direct_write_count
        >= open_cfw_test_display_direct_full_after;
}

void open_cfw_test_display_direct_write_byte(
    unsigned int instance,
    unsigned int value
)
{
    unsigned int index = open_cfw_test_display_direct_write_count;

    open_cfw_test_display_direct_write_instances[index] = instance;
    open_cfw_test_display_direct_written_values[index] = value;
    ++open_cfw_test_display_direct_write_count;
}

#define OPEN_CFW_UI_DISPLAY_DIRECT_WRITE_INSTANCE(handle) \
    ((void)(handle), open_cfw_test_display_direct_instance)
#define OPEN_CFW_UI_DISPLAY_DIRECT_WRITE_FIFO_FULL(instance) \
    open_cfw_test_display_direct_fifo_full(instance)
#define OPEN_CFW_UI_DISPLAY_DIRECT_WRITE_BYTE(instance, value) \
    open_cfw_test_display_direct_write_byte((instance), (value))

#include "../../components/apollo_main/core_overlay/ui_display_direct_write.c"
