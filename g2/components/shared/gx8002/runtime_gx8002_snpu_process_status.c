/* SPDX-License-Identifier: MIT */
/* Candidate recovery of stock status processing. Driver layout remains an
 * offset-only view; descriptor semantics and full state ownership are pending. */
#include <stdint.h>
#include <stddef.h>
#include <driver/gx_snpu.h>
struct task_callback_view {
    unsigned char unmodeled[0x90];
    GX_SNPU_CALLBACK volatile callback;
    volatile int module_id;
    void *volatile private_data;
};
_Static_assert(offsetof(struct task_callback_view, callback)==0x90,"callback offset");
_Static_assert(offsetof(struct task_callback_view, module_id)==0x94,"module offset");
_Static_assert(offsetof(struct task_callback_view, private_data)==0x98,"private offset");
extern volatile uint32_t open_cfw_gx8002_snpu_process_words[0x5e0/4];
extern uint32_t open_cfw_gx8002_npu_get_interrupt(void *,volatile uint32_t *);
extern void open_cfw_gx8002_npu_clr_interrupt_without_overflow(void *,uint32_t);
extern uint32_t open_cfw_gx8002_npu_get_over_cmd_addr(void *,uint32_t *);
extern uint32_t open_cfw_gx8002_npu_get_op_overflow_cmd_addr(void *,uint32_t *);
extern void open_cfw_gx8002_npu_clr_overflow_interrupt(void *,uint32_t);
extern int open_cfw_gx8002_snpu_suspend(void);
extern void open_cfw_gx8002_snpu_overtime_reset(void);
static inline uint32_t read_word(uint32_t offset)
{
    return *(volatile uint32_t *)((uintptr_t)open_cfw_gx8002_snpu_process_words+offset);
}
static inline void write_word(uint32_t offset,uint32_t value)
{
    *(volatile uint32_t *)((uintptr_t)open_cfw_gx8002_snpu_process_words+offset)=value;
}
static inline void *registers(void) { return (void *)(uintptr_t)read_word(0x5c4); }
int open_cfw_gx8002_snpu_process_status(void)
{
    uint32_t events;
    uint32_t completed;
    open_cfw_gx8002_npu_get_interrupt(registers(),&events);
    open_cfw_gx8002_npu_clr_interrupt_without_overflow(registers(),events);
    if (events&1) {
        open_cfw_gx8002_npu_get_over_cmd_addr(registers(),&completed);
        if (read_word(0x5d0)==completed)
            return 0;
        write_word(0x5d0,completed);
        GX_SNPU_STATE next_state=GX_SNPU_BUSY;
        uint32_t index=read_word(0x5b0);
        uint32_t end=read_word(0x5b4);
        for (;;) {
            uint32_t offset=index*144u;
            uint32_t descriptor=(uint32_t)(uintptr_t)open_cfw_gx8002_snpu_process_words+offset+16u;
            uint32_t next=index+1u;
            struct task_callback_view *record=(struct task_callback_view *)((uintptr_t)open_cfw_gx8002_snpu_process_words+offset);
            GX_SNPU_CALLBACK callback=record->callback;
            int module_id=record->module_id;
            void *private_data=record->private_data;
            index=(uint32_t)((int32_t)next%10);
            if (index==end) {
                next_state=GX_SNPU_STALL;
                open_cfw_gx8002_snpu_suspend();
            }
            if (descriptor==completed+UINT32_C(0x20000000)) {
                write_word(0,(uint32_t)next_state);
                write_word(0x5b0,index);
                if (callback) callback(module_id,next_state,private_data);
                return 0;
            }
            if (callback) callback(module_id,next_state,private_data);
        }
    }
    if (events&8) {
        open_cfw_gx8002_snpu_overtime_reset();
        return 0;
    }
    if (events&4) {
        open_cfw_gx8002_snpu_overtime_reset();
        return 0;
    }
    if (events&32) {
        open_cfw_gx8002_npu_get_op_overflow_cmd_addr(registers(),&completed);
        uint32_t mask=events;
        void *base=registers();
        (void)read_word(0x5b0); /* Original observable load before clearing. */
        open_cfw_gx8002_npu_clr_overflow_interrupt(base,mask);
        return 0;
    }
    return (events&64)?1:2;
}
