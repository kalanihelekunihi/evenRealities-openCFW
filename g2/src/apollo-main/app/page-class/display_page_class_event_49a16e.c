/* Apollo page-class event callback, native 0x49a16e..0x49a2ef. */
#include <stdint.h>

extern const uint8_t audio_uart_page_class_7561bc[];
extern uint32_t audio_uart_lv_object_event_base_4516f8(const void *, void *);
extern uint32_t audio_uart_page_event_code_450286(void *);
extern void audio_uart_page_layout_update_49a602(void *);
extern const uint8_t *audio_uart_page_metric_4993c0(void *, uint32_t);
extern int32_t audio_uart_page_metric_4993ca(void *, uint32_t);
extern int32_t audio_uart_page_metric_4993d4(void *, uint32_t);
extern int32_t audio_uart_page_metric_499360(void *, uint32_t);
extern int32_t audio_uart_page_metric_49936a(void *, uint32_t);
extern int32_t audio_uart_page_metric_499374(void *, uint32_t);
extern int32_t audio_uart_lv_obj_content_width_43fe16(void *);
extern void audio_uart_page_event_prepare_49aacc(void *);
extern void audio_uart_page_event_calculate_489546(void *, void *, int32_t,
                                                   int32_t, int32_t, int32_t,
                                                   uint32_t);
extern void audio_uart_page_event_finish_49ab06(void *, int32_t);
extern void audio_uart_page_event_extent_4519fa(void *, int32_t);
extern void audio_uart_page_event_dispatch_49a31c(void *);

static uint16_t get16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8u));
}
static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u);
    p[3] = (uint8_t)(value >> 24u);
}

void audio_uart_page_class_event_49a16e(const void *class_record, void *event) {
    (void)class_record;
    if ((uint8_t)audio_uart_lv_object_event_base_4516f8(
            audio_uart_page_class_7561bc, event) != 1u) return;
    uint32_t code = audio_uart_page_event_code_450286(event);
    uint8_t *page = (uint8_t *)(uintptr_t)get32((const uint8_t *)event);
    if (code == 0x31u || code == 0x32u) {
        audio_uart_page_layout_update_49a602(page);
        return;
    }
    if (code == 0x1bu) {
        const uint8_t *metric = audio_uart_page_metric_4993c0(page, 0u);
        int32_t value = (int32_t)get32(metric + 0x0cu);
        audio_uart_page_event_extent_4519fa(event, value / 4);
        return;
    }
    if (code == 0x34u) {
        if ((page[0x5cu] & 0x80u) != 0u) {
            const uint8_t *metric = audio_uart_page_metric_4993c0(page, 0u);
            int32_t one = (int32_t)(uintptr_t)metric;
            int32_t two = audio_uart_page_metric_4993ca(page, 0u);
            int32_t three = audio_uart_page_metric_4993d4(page, 0u);
            uint32_t options = ((page[0x5cu] & 0x20u) != 0u ? 8u : 0u) |
                               ((page[0x5cu] & 0x40u) != 0u ? 1u : 0u);
            int32_t limit;
            if ((uint32_t)audio_uart_page_metric_499360(page, 0u) == 0x3fffffffu &&
                (get16(page + 0x2au) & 0x0800u) == 0u)
                limit = 0x1fffffff;
            else
                limit = audio_uart_lv_obj_content_width_43fe16(page);
            int32_t ceiling = audio_uart_page_metric_49936a(page, 0u);
            if (limit >= ceiling)
                limit = audio_uart_page_metric_49936a(page, 0u);
            int32_t old = (int32_t)get32(page + 0x34u);
            audio_uart_page_event_prepare_49aacc(page);
            audio_uart_page_event_calculate_489546(page + 0x4cu,
                    (void *)(uintptr_t)get32(page + 0x2cu), one, two, three,
                    limit, options);
            audio_uart_page_event_finish_49ab06(page, old);
            int32_t height = audio_uart_page_metric_499374(page, 0u);
            if ((int32_t)get32(page + 0x50u) >= height)
                put32(page + 0x50u, (uint32_t)audio_uart_page_metric_499374(page, 0u));
            page[0x5cu] &= 0x7fu;
        }
        uint8_t *extent = (uint8_t *)(uintptr_t)get32((const uint8_t *)event + 0x10u);
        int32_t width = (int32_t)get32(page + 0x4cu);
        if (width >= (int32_t)get32(extent)) put32(extent, (uint32_t)width);
        int32_t height = (int32_t)get32(page + 0x50u);
        if (height >= (int32_t)get32(extent + 4u))
            put32(extent + 4u, (uint32_t)height);
        return;
    }
    if (code == 0x1du)
        audio_uart_page_event_dispatch_49a31c(event);
}
