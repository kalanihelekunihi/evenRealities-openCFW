unsigned int open_cfw_test_display_direct_read_instance;
unsigned int open_cfw_test_display_direct_read_empty_after;
unsigned int open_cfw_test_display_direct_read_status_checks;
unsigned int open_cfw_test_display_direct_read_status_instances[16];
unsigned int open_cfw_test_display_direct_read_word_count;
unsigned int open_cfw_test_display_direct_read_word_instances[16];
unsigned int open_cfw_test_display_direct_read_words[16];

void open_cfw_test_display_direct_read_reset(void)
{
    unsigned int index;

    open_cfw_test_display_direct_read_instance = 3U;
    open_cfw_test_display_direct_read_empty_after = 16U;
    open_cfw_test_display_direct_read_status_checks = 0U;
    open_cfw_test_display_direct_read_word_count = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_display_direct_read_status_instances[index] = 0U;
        open_cfw_test_display_direct_read_word_instances[index] = 0U;
        open_cfw_test_display_direct_read_words[index] = 0U;
    }
}

unsigned int open_cfw_test_display_direct_read_fifo_empty(
    unsigned int instance
)
{
    unsigned int check =
        open_cfw_test_display_direct_read_status_checks;

    open_cfw_test_display_direct_read_status_instances[check] = instance;
    ++open_cfw_test_display_direct_read_status_checks;
    return open_cfw_test_display_direct_read_word_count
        >= open_cfw_test_display_direct_read_empty_after;
}

unsigned int open_cfw_test_display_direct_read_word(
    unsigned int instance
)
{
    unsigned int index =
        open_cfw_test_display_direct_read_word_count;

    open_cfw_test_display_direct_read_word_instances[index] = instance;
    ++open_cfw_test_display_direct_read_word_count;
    return open_cfw_test_display_direct_read_words[index];
}

#define OPEN_CFW_UI_DISPLAY_DIRECT_READ_INSTANCE(handle) \
    ((void)(handle), open_cfw_test_display_direct_read_instance)
#define OPEN_CFW_UI_DISPLAY_DIRECT_READ_FIFO_EMPTY(instance) \
    open_cfw_test_display_direct_read_fifo_empty(instance)
#define OPEN_CFW_UI_DISPLAY_DIRECT_READ_WORD(instance) \
    open_cfw_test_display_direct_read_word(instance)

#include "../../components/apollo_main/core_overlay/ui_display_direct_read.c"
