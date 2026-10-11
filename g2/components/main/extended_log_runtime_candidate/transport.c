/* Experimental stock-derived transport wrappers 0x448d4e/0x4495e4.
 * Queue and event-group children remain typed source/data contracts. */
#include <stdint.h>
#include <stdbool.h>

/* 0x448fc4 and 0x448fc8 literals in the locked Apollo image. */
static volatile uint8_t *const enabled = (volatile uint8_t *)(uintptr_t)0x20074fc0u;
static volatile uint8_t *const default_level = (volatile uint8_t *)(uintptr_t)0x20004546u;
extern uint8_t *g2_log_transport_node_allocate(void); /* >=269 writable bytes */
extern uint32_t g2_log_transport_node_enqueue(uint8_t *node); /* 0=failure */
extern void g2_log_transport_node_free(uint8_t *node);
extern const char g2_log_transport_queue_failure_message[];
extern int32_t g2_log_transport_queue_failure(const char *message,...);

void g2_log_transport_submit(uint32_t source_address,uint32_t length,
                             uint32_t level,uint32_t mode)
{
    if (!*enabled || !source_address || !length) return;
    if ((uint8_t)level == 0u) level = *default_level;
    if (length > 255u) length = 255u;
    uint8_t *node = g2_log_transport_node_allocate();
    if (!node) return;
    const uint8_t *source = (const uint8_t *)(uintptr_t)source_address;
    for (uint32_t i = 0; i < length; ++i) node[13u+i] = source[i];
    node[13u+length] = 0u;
    node[8] = (uint8_t)length; node[9] = 0;
    node[10] = (uint8_t)level; node[11] = 0;
    node[12] = (uint8_t)mode;
    if (g2_log_transport_node_enqueue(node) == 0u) {
        g2_log_transport_node_free(node);
        g2_log_transport_queue_failure(g2_log_transport_queue_failure_message);
    }
}

extern uint32_t audio_irq_context(void);
extern uint32_t g2_log_event_set_task(uint32_t event_handle,uint32_t bits);
extern uint32_t g2_log_event_set_isr(uint32_t event_handle,uint32_t bits,uint32_t *woken);
extern uint32_t g2_log_event_get_bits(uint32_t event_handle);
static uint32_t signal_status(uint32_t event_handle,uint32_t bits)
{
    if (event_handle == 0u || (bits & 0xff000000u)) return 0xfffffffcu;
    if (audio_irq_context() != 0u) {
        uint32_t woken = 0u;
        if (g2_log_event_set_isr(event_handle,bits,&woken) == 0u) return 0xfffffffdu;
        uint32_t result = bits | g2_log_event_get_bits(event_handle);
        if (woken != 0u)
            *(volatile uint32_t *)(uintptr_t)0xe000ed04u = 0x10000000u;
        return result;
    }
    return g2_log_event_set_task(event_handle,bits);
}
void g2_log_transport_signal(uint32_t event_handle,uint32_t bits)
{
    (void)signal_status(event_handle,bits);
}
