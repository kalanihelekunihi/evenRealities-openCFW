unsigned char open_cfw_test_sink_active[4];
unsigned char open_cfw_test_sink_acknowledged[4];
void *open_cfw_test_sink_handles[4];
unsigned char open_cfw_test_sink_descriptor[56];
const void *open_cfw_test_sink_buffer;
void *open_cfw_test_sink_submitted_handle;
unsigned int open_cfw_test_sink_selected_channel;
unsigned int open_cfw_test_sink_submit_count;
unsigned int open_cfw_test_sink_submit_result;
unsigned int open_cfw_test_sink_ack_on_submit;
unsigned int open_cfw_test_sink_ack_after_delay;
unsigned int open_cfw_test_sink_delay_count;
unsigned int open_cfw_test_sink_delay_value;

void open_cfw_test_sink_reset(void)
{
    unsigned int index;

    for (index = 0; index < 4U; ++index) {
        open_cfw_test_sink_active[index] = 0U;
        open_cfw_test_sink_acknowledged[index] = 0xA5U;
        open_cfw_test_sink_handles[index] =
            (void *)(unsigned long)(0x1000U + index);
    }
    for (index = 0; index < 56U; ++index) {
        open_cfw_test_sink_descriptor[index] = 0xA5U;
    }
    open_cfw_test_sink_buffer = (const void *)0;
    open_cfw_test_sink_submitted_handle = (void *)0;
    open_cfw_test_sink_selected_channel = 0xFFFFFFFFU;
    open_cfw_test_sink_submit_count = 0U;
    open_cfw_test_sink_submit_result = 0U;
    open_cfw_test_sink_ack_on_submit = 0U;
    open_cfw_test_sink_ack_after_delay = 0xFFFFFFFFU;
    open_cfw_test_sink_delay_count = 0U;
    open_cfw_test_sink_delay_value = 0U;
}

void open_cfw_test_sink_set_buffer(
    unsigned int words[14],
    const void *buffer
)
{
    words[0] = 0xA1B2C3D4U;
    open_cfw_test_sink_buffer = buffer;
}

void *open_cfw_test_sink_handle(unsigned int channel)
{
    open_cfw_test_sink_selected_channel = channel;
    return open_cfw_test_sink_handles[channel];
}

int open_cfw_test_sink_submit(void *handle, const void *descriptor)
{
    const unsigned char *bytes = descriptor;
    unsigned int index;

    ++open_cfw_test_sink_submit_count;
    open_cfw_test_sink_submitted_handle = handle;
    for (index = 0; index < 56U; ++index) {
        open_cfw_test_sink_descriptor[index] = bytes[index];
    }
    if (open_cfw_test_sink_ack_on_submit != 0U) {
        open_cfw_test_sink_acknowledged[
            open_cfw_test_sink_selected_channel
        ] = (unsigned char)open_cfw_test_sink_ack_on_submit;
    }
    return (int)open_cfw_test_sink_submit_result;
}

void open_cfw_test_sink_delay(unsigned int milliseconds)
{
    ++open_cfw_test_sink_delay_count;
    open_cfw_test_sink_delay_value = milliseconds;
    if (
        open_cfw_test_sink_delay_count
            == open_cfw_test_sink_ack_after_delay
    ) {
        open_cfw_test_sink_acknowledged[
            open_cfw_test_sink_selected_channel
        ] = 1U;
    }
}

#define OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_ACTIVE(channel) \
    open_cfw_test_sink_active[channel]
#define OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_ACKNOWLEDGED(channel) \
    open_cfw_test_sink_acknowledged[channel]
#define OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_HANDLE(channel) \
    open_cfw_test_sink_handle(channel)
#define OPEN_CFW_UI_DISPLAY_SINK_DESCRIPTOR_SET_BUFFER(words, buffer) \
    open_cfw_test_sink_set_buffer((words), (buffer))
#define OPEN_CFW_UI_DISPLAY_SINK_SUBMIT(handle, descriptor) \
    open_cfw_test_sink_submit((handle), (descriptor))
#define OPEN_CFW_UI_DISPLAY_SINK_DELAY(milliseconds) \
    open_cfw_test_sink_delay(milliseconds)

#include "../../components/apollo_main/core_overlay/ui_display_sink.c"
