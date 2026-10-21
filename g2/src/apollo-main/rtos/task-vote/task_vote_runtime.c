/* Native task vote graph 0x46d67c..0x46d836, 32 eight-byte slots. */
#include <stdint.h>

extern volatile uint8_t audio_task_vote_state_200700e0[];
extern void *receiver_current_task(void); /* selected xTaskGetCurrentTaskHandle */
extern uint32_t g2_gpio_critical_save(void); /* selected 0x473940 */
extern void g2_power_critical_restore(uint32_t); /* selected MSR PRIMASK */

static uint32_t load_word(unsigned offset)
{
    return *(volatile uint32_t *)(void *)(audio_task_vote_state_200700e0+offset);
}
static void store_word(unsigned offset,uint32_t value)
{
    *(volatile uint32_t *)(void *)(audio_task_vote_state_200700e0+offset)=value;
}

int32_t task_vote_find_slot(uint32_t handle)
{
    for (unsigned i=0;i<32u;++i)
        if (load_word(i*8u)==handle) return (int32_t)i;
    return -1;
}

int32_t task_vote_find_free_slot(void)
{
    for (unsigned i=0;i<32u;++i)
        if (load_word(i*8u)==0u) return (int32_t)i;
    return -1;
}

uint32_t task_vote_acquire_for_handle(uint32_t handle)
{
    if (audio_task_vote_state_200700e0[0x104u]==0u || handle==0u) return 0u;
    uint32_t prior=g2_gpio_critical_save();
    int32_t slot=task_vote_find_slot(handle);
    uint32_t acquired=0u;
    if (slot<0) {
        slot=task_vote_find_free_slot();
        if (slot>=0) {
            store_word((unsigned)slot*8u,handle);
            audio_task_vote_state_200700e0[(unsigned)slot*8u+4u]=1u;
            store_word(0x100u,load_word(0x100u)+1u);
            acquired=1u;
        }
    } else if (audio_task_vote_state_200700e0[(unsigned)slot*8u+4u]==0u) {
        audio_task_vote_state_200700e0[(unsigned)slot*8u+4u]=1u;
        store_word(0x100u,load_word(0x100u)+1u);
        acquired=1u;
    }
    g2_power_critical_restore(prior);
    return acquired;
}

uint32_t task_vote_release_for_handle(uint32_t handle)
{
    if (audio_task_vote_state_200700e0[0x104u]==0u || handle==0u) return 0u;
    uint32_t prior=g2_gpio_critical_save();
    int32_t slot=task_vote_find_slot(handle);
    uint32_t released=0u;
    if (slot>=0 && audio_task_vote_state_200700e0[(unsigned)slot*8u+4u]==1u) {
        audio_task_vote_state_200700e0[(unsigned)slot*8u+4u]=0u;
        store_word(0x100u,load_word(0x100u)-1u);
        released=1u;
    }
    g2_power_critical_restore(prior);
    return released;
}

void task_vote_acquire_current(void)
{
    uint32_t handle=(uint32_t)(uintptr_t)receiver_current_task();
    if (handle!=0u) (void)task_vote_acquire_for_handle(handle);
}

void task_vote_release_current(void)
{
    uint32_t handle=(uint32_t)(uintptr_t)receiver_current_task();
    if (handle!=0u) (void)task_vote_release_for_handle(handle);
}
