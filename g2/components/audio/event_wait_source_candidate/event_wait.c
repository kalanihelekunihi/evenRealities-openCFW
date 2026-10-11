/* Experimental CMSIS osEventFlagsWait outer body, stock 0x44969c.
 * FreeRTOS xEventGroupWaitBits remains a typed lower source contract. */
#include <stdint.h>
extern uint32_t audio_irq_context(void);
extern uint32_t g2_event_wait_bits(uint32_t handle,uint32_t bits,
                                    uint32_t clear_on_exit,uint32_t wait_all,
                                    uint32_t timeout);
uint32_t osEventFlagsWait(uint32_t handle,uint32_t bits,
                          uint32_t options,uint32_t timeout) {
    if(!handle || (bits&0xff000000u)) return 0xfffffffcu;
    if(audio_irq_context()!=0u)
        return timeout==0u?0xfffffffau:0xfffffffcu;
    uint32_t got=g2_event_wait_bits(handle,bits,
                                     (options&2u)?0u:1u,
                                     (options&1u)?1u:0u,timeout);
    int matched=(options&1u)?((got&bits)==bits):((got&bits)!=0u);
    return matched?got:(timeout?0xfffffffeu:0xfffffffdu);
}
uint32_t audio_event_wait(uint32_t,uint32_t,uint32_t,uint32_t)
    __attribute__((alias("osEventFlagsWait")));
