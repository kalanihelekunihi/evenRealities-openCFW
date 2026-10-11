/* Native CMSIS osMutexNew 0x44971c and osEventFlagsNew 0x449590. */
#include <stdint.h>
#include <stddef.h>
extern uint32_t audio_irq_context(void); /* selected 0x44900e */
extern void *audio_uart_mutex_dynamic_create(uint32_t type); /* 0x4416d6 */
extern void *audio_uart_mutex_static_create(uint32_t type,void *memory); /* 0x4416f0 */
extern void *audio_uart_event_dynamic_create(void); /* 0x47ebd8 */
extern void *audio_uart_event_static_create(void *memory); /* 0x47eb94 */
static uint32_t field32(const void *p,uint32_t offset) {return *(const uint32_t *)((const uint8_t *)p+offset);}
void *audio_uart_mutex_new(const void *attributes)
{
    if (audio_irq_context()!=0u) return 0;
    uint32_t flags=attributes ? field32(attributes,4u) : 0u;
    if (flags&8u) return 0;
    uint32_t recursive=flags&1u;
    uint32_t storage_kind=0u;
    if (attributes) {
        void *storage=(void *)(uintptr_t)field32(attributes,8u);
        uint32_t size=field32(attributes,12u);
        if (storage && size>=80u) storage_kind=1u;
        else if (!storage && size==0u) storage_kind=0u;
        else return 0;
    }
    void *mutex=storage_kind ? audio_uart_mutex_static_create(recursive?4u:1u,(void *)(uintptr_t)field32(attributes,8u))
                             : audio_uart_mutex_dynamic_create(recursive?4u:1u);
    if (mutex && recursive) mutex=(void *)((uintptr_t)mutex|1u);
    return mutex;
}
void *audio_uart_event_new(const void *attributes)
{
    if (audio_irq_context()!=0u) return 0;
    uint32_t storage_kind=0u;
    if (attributes) {
        void *storage=(void *)(uintptr_t)field32(attributes,8u);
        uint32_t size=field32(attributes,12u);
        if (storage && size>=32u) storage_kind=1u;
        else if (!storage && size==0u) storage_kind=0u;
        else return 0;
    }
    return storage_kind ? audio_uart_event_static_create((void *)(uintptr_t)field32(attributes,8u))
                        : audio_uart_event_dynamic_create();
}
