/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 Apollo four-channel asynchronous
 * display sink at 0x0055E7FA. The exact stock boundary, channel state, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

typedef void (*open_cfw_ui_display_sink_delay_fn)(
    unsigned int microseconds
);

unsigned int open_cfw_ui_display_submit(
    void *handle,
    const void *descriptor
);

#ifndef OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_BASE
#define OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_BASE \
    ((volatile unsigned char *)0x20000D2CU)
#endif

#ifndef OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_ACTIVE
#define OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_ACTIVE(channel) \
    (OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_BASE[(channel) * 0x1CU + 0x18U])
#endif

#ifndef OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_ACKNOWLEDGED
#define OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_ACKNOWLEDGED(channel) \
    (OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_BASE[(channel) * 0x1CU + 0x19U])
#endif

#ifndef OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_HANDLE
#define OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_HANDLE(channel) \
    (*(void * volatile *)(void *)( \
        OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_BASE \
            + (channel) * 0x1CU + 4U \
    ))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_SINK_DESCRIPTOR_SET_BUFFER
#define OPEN_CFW_UI_DISPLAY_SINK_DESCRIPTOR_SET_BUFFER(words, buffer) \
    ((words)[0] = (unsigned int)(buffer))
#endif

#ifndef OPEN_CFW_UI_DISPLAY_SINK_SUBMIT
#define OPEN_CFW_UI_DISPLAY_SINK_SUBMIT(handle, descriptor) \
    open_cfw_ui_display_submit( \
        (handle), \
        (descriptor) \
    )
#endif

#ifndef OPEN_CFW_UI_DISPLAY_SINK_DELAY
#define OPEN_CFW_UI_DISPLAY_SINK_DELAY(microseconds) \
    (((open_cfw_ui_display_sink_delay_fn)0x00491103U)(microseconds))
#endif

/*
 * Stock ABI at 0x0055E7FA. The selector is truncated to eight bits, only four
 * channels are accepted, and an active channel submits a 56-byte descriptor
 * before polling its acknowledgement byte at 10-microsecond intervals.
 */
__attribute__((used, noinline))
unsigned int open_cfw_ui_display_sink(
    unsigned int selector,
    const void *buffer,
    unsigned int length
)
{
    union {
        unsigned int words[14];
        unsigned char bytes[56];
    } descriptor;
    unsigned int channel = (unsigned char)selector;
    unsigned int index;
    unsigned int polls;
    int result;

    if (channel >= 4U) {
        return 1U;
    }
    if (OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_ACTIVE(channel) != 1U) {
        return 1U;
    }

    for (index = 0; index < 14U; ++index) {
        descriptor.words[index] = 0U;
    }
    OPEN_CFW_UI_DISPLAY_SINK_DESCRIPTOR_SET_BUFFER(
        descriptor.words,
        buffer
    );
    descriptor.words[1] = length;

    OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_ACKNOWLEDGED(channel) = 0U;
    result = OPEN_CFW_UI_DISPLAY_SINK_SUBMIT(
        OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_HANDLE(channel),
        descriptor.bytes
    );

    polls = 0U;
    while (
        polls < 1000U
            && OPEN_CFW_UI_DISPLAY_SINK_CHANNEL_ACKNOWLEDGED(channel) != 1U
    ) {
        OPEN_CFW_UI_DISPLAY_SINK_DELAY(10U);
        ++polls;
    }
    return result == 0 ? 0U : 1U;
}
