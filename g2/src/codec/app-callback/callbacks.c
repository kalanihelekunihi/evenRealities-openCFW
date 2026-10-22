/* Experimental C projection of authenticated XIP child entries
 * 0x1020975c and 0x10209770. Source is Ghidra/native instruction evidence,
 * not the public sample app. Child contracts remain external. */
#include "request.h"
#include "resident_sample_product_data.h"

/* Stack-byte pointer lifetime depends on the actual queue/ROM consumer;
 * synchronous payload copying has not been established. */
/* Both stock call sites use a literal structure address, not a pointer cell.
 * Its runtime contents remain product state, not zero-filled source data. */
static g2_codec_request *const g2_codec_request_cell =
    &gx8002_request_initial_26d5c.request;
extern uint32_t g2_codec_timestamp(void); /* resident 0x10025930 */

/* Stock 0x10205F88 (gx_gpio_set_level) */
uint32_t g2_codec_gpio_set_level(uint32_t pin, uint32_t level) {
    volatile uint32_t *const output =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0001004);
    const uint32_t mask = UINT32_C(1) << (pin & UINT32_C(31));
    const uint32_t previous = *output;
    *output = level == 0 ? previous & ~mask : previous | mask;
    return 0u;
}

/* Native-checked source reductions of 0x102093dc and 0x102093f4. */
/* Stock 0x102093DC (gx8002_notification_stamp) */
void g2_codec_event_prepare(void) {
    g2_codec_gpio_set_level(2u, 0u);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e910) =
        g2_codec_timestamp();
}

/* Stock 0x102093F4 (gx8002_app_reply) */
uint32_t g2_codec_event_dispatch(uint32_t kind, uint32_t code, uint32_t argument) {
    volatile g2_codec_request *request = g2_codec_request_cell;
    *(volatile uint16_t *)(uintptr_t)UINT32_C(0x2002e914) = (uint16_t)argument;
    const uint16_t request_code = (uint16_t)(code | (kind == 1u ? 0x300u : 0x200u));
    request->flag = 1u;
    request->payload = (const uint8_t *)(uintptr_t)UINT32_C(0x2002e914);
    request->request_code = request_code;
    request->count = 2u;
    g2_codec_request_consume(g2_codec_request_cell);
    return 0u;
}

/* Stock 0x1020975C (gx8002_event_notify) */
void g2_codec_event_91_helper(uint32_t event_argument) {
    g2_codec_event_prepare();
    g2_codec_event_dispatch(1u, 12u, event_argument);
}

/* Stock 0x10209770 (gx8002_i2s_ack) */
void g2_codec_construct_request(void) {
    uint8_t one = 1;
    g2_codec_request *request = g2_codec_request_cell;
    request->payload = &one;
    request->request_code = 0x10fu;
    request->flag = 1u;
    request->count = 1u;
    g2_codec_request_consume(request);
}
