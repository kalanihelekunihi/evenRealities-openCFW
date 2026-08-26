/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room source replacement for the G2 2.2.6.10 case-UART manager in
 * platform\device_mgr\box_uart_mgr.c.  The retained UART, device-manager,
 * product-test, delay, and asynchronous sink ABIs are documented in
 * docs/research/g2-box-uart-mgr-recovery.md.
 */

typedef unsigned char open_cfw_box_u8;
typedef unsigned short open_cfw_box_u16;

typedef struct {
    open_cfw_box_u16 type;
    open_cfw_box_u16 length;
    const open_cfw_box_u8 *data;
} open_cfw_box_uart_record;

void *open_cfw_retained_box_uart_memcpy(
    void *destination,
    const void *source,
    unsigned int length
);
void *open_cfw_retained_box_uart_memset(
    void *destination,
    int value,
    unsigned int length
);
int open_cfw_retained_box_uart_queue(const open_cfw_box_uart_record *record);
int open_cfw_retained_box_uart_register_receive(
    unsigned int channel,
    void (*callback)(const open_cfw_box_u8 *, unsigned int)
);
int open_cfw_retained_box_uart_resume(unsigned int channel);
int open_cfw_retained_box_uart_start(unsigned int channel);
int open_cfw_retained_box_uart_stop(unsigned int channel);
int open_cfw_retained_box_uart_clear(unsigned int channel);
int open_cfw_retained_box_uart_flush(unsigned int channel);
int open_cfw_retained_box_uart_product_test(
    const open_cfw_box_u8 *request,
    unsigned int request_length,
    open_cfw_box_u8 *response,
    open_cfw_box_u8 *response_length
);
int open_cfw_retained_box_uart_execute(
    const open_cfw_box_u8 *request,
    unsigned int request_length,
    const open_cfw_box_u8 *response,
    unsigned int response_length
);
int open_cfw_retained_box_uart_delay(unsigned int ticks);
unsigned int open_cfw_ui_display_sink(
    unsigned int selector,
    const void *buffer,
    unsigned int length
);
int open_cfw_box_uart_unpack(
    const open_cfw_box_uart_record *record,
    open_cfw_box_u8 *output,
    open_cfw_box_u8 *output_length
);
unsigned int open_cfw_box_uart_send(
    unsigned int selector,
    const open_cfw_box_u8 *buffer,
    unsigned int length
);
void open_cfw_box_uart_receive(
    const open_cfw_box_u8 *data,
    unsigned int length
);
#if defined(__arm__) || defined(__thumb__)
__asm__(".type open_cfw_box_uart_receive,%function");
#endif

#ifndef OPEN_CFW_BOX_UART_RX_SLOT
#define OPEN_CFW_BOX_UART_RX_SLOT \
    (*(volatile open_cfw_box_u8 *)0x20074F96U)
#endif

#ifndef OPEN_CFW_BOX_UART_RX_BUFFER
#define OPEN_CFW_BOX_UART_RX_BUFFER(slot) \
    ((open_cfw_box_u8 *)0x2005BA68U + (unsigned int)(slot) * 1024U)
#endif

#if !defined(OPEN_CFW_BOX_UART_UNPACK_ONLY) && \
    !defined(OPEN_CFW_BOX_UART_SEND_ONLY) && \
    !defined(OPEN_CFW_BOX_UART_RECEIVE_ONLY) && \
    !defined(OPEN_CFW_BOX_UART_INIT_ONLY) && \
    !defined(OPEN_CFW_BOX_UART_HANDLE_ONLY)
#define OPEN_CFW_BOX_UART_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_BOX_UART_BUILD_ALL) || \
    defined(OPEN_CFW_BOX_UART_UNPACK_ONLY)
__attribute__((used, noinline))
int open_cfw_box_uart_unpack(
    const open_cfw_box_uart_record *record,
    open_cfw_box_u8 *output,
    open_cfw_box_u8 *output_length
)
{
    const open_cfw_box_u8 *input;
    unsigned int index;
    unsigned int remaining;
    unsigned int checksum;
    unsigned int checksum_index;

    if (record == (const open_cfw_box_uart_record *)0 || record->length == 0U) {
        return -1;
    }

    input = record->data;
    index = 0U;
    while (index < record->length && input[index] == 0U) {
        ++index;
    }
    if (index == record->length) {
        return 0;
    }

    remaining = (unsigned int)record->length - index;
    if (input[index] != 0x54U) {
        checksum = remaining + 0x7DU;
        checksum_index = 0U;
        while (checksum_index + 1U < remaining) {
            checksum += input[index + checksum_index];
            ++checksum_index;
        }
        if ((open_cfw_box_u8)checksum != input[index + remaining - 1U]) {
            return -3;
        }
    }

    open_cfw_retained_box_uart_memcpy(output, input + index, remaining);
    *output_length = (open_cfw_box_u8)remaining;
    return 0;
}
#endif

#if defined(OPEN_CFW_BOX_UART_BUILD_ALL) || \
    defined(OPEN_CFW_BOX_UART_SEND_ONLY)
__attribute__((used, noinline))
unsigned int open_cfw_box_uart_send(
    unsigned int selector,
    const open_cfw_box_u8 *buffer,
    unsigned int length
)
{
    return open_cfw_ui_display_sink(
        (open_cfw_box_u8)selector,
        buffer,
        (open_cfw_box_u8)length
    );
}
#endif

#if defined(OPEN_CFW_BOX_UART_BUILD_ALL) || \
    defined(OPEN_CFW_BOX_UART_RECEIVE_ONLY)
__attribute__((used, noinline))
void open_cfw_box_uart_receive(
    const open_cfw_box_u8 *data,
    unsigned int length
)
{
    open_cfw_box_uart_record record;
    open_cfw_box_u8 slot;
    open_cfw_box_u8 *buffer;

    if (length < 3U || length > 1024U) {
        return;
    }

    slot = OPEN_CFW_BOX_UART_RX_SLOT;
    if (slot >= 5U) {
        slot = 0U;
    }
    buffer = OPEN_CFW_BOX_UART_RX_BUFFER(slot);
    open_cfw_retained_box_uart_memcpy(buffer, data, length);
    if (length < 1024U) {
        open_cfw_retained_box_uart_memset(buffer + length, 0, 1024U - length);
    }
    OPEN_CFW_BOX_UART_RX_SLOT = (open_cfw_box_u8)((slot + 1U) % 5U);

    record.type = 1U;
    record.length = (open_cfw_box_u16)length;
    record.data = buffer;
    (void)open_cfw_retained_box_uart_queue(&record);
}
#endif

#if defined(OPEN_CFW_BOX_UART_BUILD_ALL) || \
    defined(OPEN_CFW_BOX_UART_INIT_ONLY)
__attribute__((used, noinline))
void open_cfw_box_uart_init(void)
{
    (void)open_cfw_retained_box_uart_register_receive(
        2U,
        open_cfw_box_uart_receive
    );
    (void)open_cfw_retained_box_uart_resume(2U);
    (void)open_cfw_retained_box_uart_start(2U);
}
#endif

#if defined(OPEN_CFW_BOX_UART_BUILD_ALL) || \
    defined(OPEN_CFW_BOX_UART_HANDLE_ONLY)
__attribute__((used, noinline))
void open_cfw_box_uart_handle(const open_cfw_box_uart_record *record)
{
    open_cfw_box_u8 request[1024];
    open_cfw_box_u8 response[256];
    open_cfw_box_u8 request_length = 0U;
    open_cfw_box_u8 response_length = 0U;
    int result;

    if (record == (const open_cfw_box_uart_record *)0 || record->length == 0U) {
        return;
    }

    open_cfw_retained_box_uart_memset(request, 0, sizeof(request));
    open_cfw_retained_box_uart_memset(response, 0, sizeof(response));

    result = open_cfw_retained_box_uart_stop(2U);
    if (result == 0) {
        (void)open_cfw_retained_box_uart_clear(2U);
        result = open_cfw_box_uart_unpack(record, request, &request_length);
        if (result == 0) {
            result = open_cfw_retained_box_uart_product_test(
                request,
                request_length,
                response,
                &response_length
            );
            if (result == 0) {
                (void)open_cfw_retained_box_uart_delay(2U);
                result = (int)open_cfw_box_uart_send(
                    2U,
                    response,
                    response_length
                );
                if (result == 0) {
                    (void)open_cfw_retained_box_uart_flush(2U);
                }
            }
        }
    }

    result = open_cfw_retained_box_uart_start(2U);
    if (result == 0) {
        (void)open_cfw_retained_box_uart_execute(
            request,
            request_length,
            response,
            response_length
        );
    }
}
#endif
