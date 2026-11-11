/* Native clock-update contracts use ordinary C and the shared clock owners. */
#include "../../vendor/time_calendar/time_calendar.h"
#include "../board/native_clock_bootstrap.h"
#include "../board/native_battery_memory.h"
extern time_calendar_state r1_time_state;
extern time_calendar_registration r1_time_registration;
extern void __aeabi_memclr(void *,uint32_t);
_Static_assert(offsetof(time_calendar_state,time_update_pending)==11,"native pending flag");

__attribute__((section(".text.r1_event_service_0008aea4")))
uint32_t r1_event_service_0008aea4(void)
{
    ((volatile time_calendar_state *)&r1_time_state)->time_update_pending=1;
    return 1;
}

uint32_t r1_event_service_0008aeb0(uint32_t epoch,int32_t offset)
{
    volatile uint8_t *state=(volatile uint8_t *)&r1_time_state;
    volatile uint8_t *registration=(volatile uint8_t *)&r1_time_registration;
    /* The snapshot exposes these two output slots to the backend. Reload
     * them after get; the cached pending decision remains independent of
     * later changes to the shared registration byte. */
    volatile struct {
        void *context;
        const r1_native_clock_ops *ops;
        uint32_t pending;
    } frame;
    if (!state[10]) return 0;
    if (!r1_clock_backend_snapshot((const r1_native_clock_ops **)&frame.ops,
            (void **)&frame.context)) return 0;
    const r1_native_clock_ops *initial_ops=frame.ops;
    if (!initial_ops || !read32((const volatile uint8_t *)initial_ops+16)) return 0;
    if ((int32_t)(int16_t)read16(state+8)!=offset) {
        write16(state+8,(uint32_t)offset);
        __aeabi_memclr((void *)(uintptr_t)(state+12),20);
    }
    uint32_t old_time=0;
    frame.pending=registration[0]^1u;
    if (frame.pending) {
        uint32_t (*get)(void *)=(uint32_t (*)(void *))(uintptr_t)
            read32((const volatile uint8_t *)initial_ops+8);
        if (get) old_time=get(frame.context);
    }
    int32_t (*update)(uint32_t,int32_t,void *)=frame.ops->prefix.update;
    uint32_t result=(uint32_t)update(epoch,offset,frame.context);
    if (result) {
        __aeabi_memclr((void *)(uintptr_t)(state+12),20);
        if (frame.pending) {
            write32(registration+4,old_time);
            registration[0]=1;
        }
    }
    return result;
}
