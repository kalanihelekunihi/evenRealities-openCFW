/* Typed source data for native thread-pool CMSIS attributes 0x77ccac and
 * 0x75bd00. Pointer relocations replace stock addresses; backing RAM remains
 * an explicit linker/product placement contract. */
#include <stdint.h>
struct pool_queue_attrs {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
    void *mq_mem; uint32_t mq_size;
};
struct pool_thread_attrs {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
    void *stack_mem; uint32_t stack_size; uint32_t priority;
    uint32_t tz_module; uint32_t reserved;
};
_Static_assert(sizeof(struct pool_queue_attrs)==24u,"queue attributes ABI");
_Static_assert(sizeof(struct pool_thread_attrs)==36u,"thread attributes ABI");
extern uint8_t audio_uart_pool_queue_control_mem[0x50]; /* 0x20072e98 */
extern uint8_t audio_uart_pool_queue_storage[0xbb8]; /* 0x203737c0 */
static const char queue_name[]="threadpool_Queue"; /* 0x784388 */
const struct pool_queue_attrs audio_uart_pool_queue_attrs={
    queue_name,0u,audio_uart_pool_queue_control_mem,0x50u,
    audio_uart_pool_queue_storage,0xbb8u};
const struct pool_thread_attrs audio_uart_pool_thread_attrs={
    0,0u,0,0u,0,0x1000u,0x2bu,0u,0u};
