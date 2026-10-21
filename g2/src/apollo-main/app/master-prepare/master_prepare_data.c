/* Native SyncScheduleManagerInit 0x45d1ec source data and CMSIS attrs. */
#include <stdint.h>

struct queue_attrs {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
    void *mq_mem; uint32_t mq_size;
};
struct thread_attrs {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
    void *stack_mem; uint32_t stack_size; uint32_t priority;
    uint32_t tz_module; uint32_t reserved;
};
_Static_assert(sizeof(struct queue_attrs)==24u,"queue attributes ABI");
_Static_assert(sizeof(struct thread_attrs)==36u,"thread attributes ABI");

void *audio_uart_master_schedule_queue; /* native 0x200749d0 */
_Alignas(4) uint8_t audio_uart_master_queue_control_mem[0x50]; /* 0x20072e48 */
_Alignas(4) uint8_t audio_uart_master_queue_storage[0x258]; /* 0x2006eab8 */
static const char queue_name[]="syncScheduleMgr_queue";
static const char thread_name[]="sync_schedule_mgr";
static const struct queue_attrs queue_attributes={
    queue_name,0u,audio_uart_master_queue_control_mem,0x50u,
    audio_uart_master_queue_storage,0x258u};
const void *audio_uart_master_queue_attrs=&queue_attributes;
const struct thread_attrs audio_uart_master_thread_attrs={
    thread_name,0u,0,0u,0,0x1000u,0x29u,0u,0u};

const char audio_uart_master_function[]="SyncScheduleManagerInit";
const char audio_uart_master_e_queue[]="create schedule manager queue failed.";
const char audio_uart_master_c_queue[]="[sync.module.framework]create schedule manager queue failed.";
const char audio_uart_master_e_thread[]="create schedule manager thread failed.";
const char audio_uart_master_c_thread[]="[sync.module.framework]create schedule manager thread failed.";
const char audio_uart_master_e_ready[]="sync schedule manager initialized successfully";
const char audio_uart_master_c_ready[]="[sync.module.framework]sync schedule manager initialized successfully";
