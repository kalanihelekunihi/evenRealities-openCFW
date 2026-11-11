#include <stdint.h>

/* Native 0x329574..0x32960e: associated link completion. A role-3 link
 * still waiting (+629/+630, +620, +360) only signals the auxiliary hook.
 * Otherwise: notify the registered close hook (+24 of 0x805cd8) with the
 * link index, reset the associated state and query the radio for the
 * handle at +566 (no answer: signal). When the report hook (0x8052cc) and
 * +109 are set, report either the 1-byte status (+262, mode 1) or the
 * 64-bit value at +464 (mode 0). Finally restart the radio request with
 * the handle + 6. */
extern uint32_t opencfw_em9305_associated_reset_32ae50(uintptr_t link);
extern uint32_t opencfw_em9305_radio_query_3253a4(uint32_t handle);
extern uint32_t opencfw_em9305_auxiliary_signal_304394(void);
extern uint32_t opencfw_em9305_radio_request_start_303cd8(uint32_t request, uint32_t handle);

uint32_t opencfw_em9305_associated_callback_329574(uintptr_t owner)
{
    uintptr_t link=*(volatile uint32_t *)(owner+36u);
    if(*(volatile uint8_t *)(link+1u)==3u){
        if(*(volatile uint8_t *)(link+629u)!=0u){
            if(*(volatile uint8_t *)(link+630u)!=0u)
                return opencfw_em9305_auxiliary_signal_304394();
        }else if(*(volatile uint8_t *)(link+620u)==0u||
                 *(volatile uint32_t *)(link+360u)==0u){
            return opencfw_em9305_auxiliary_signal_304394();
        }
    }
    uintptr_t hooks=*(volatile uint32_t *)(uintptr_t)0x805cd8u;
    if(hooks!=0u){
        uintptr_t close=*(volatile uint32_t *)(hooks+24u);
        if(close!=0u){
            uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
            int32_t index=(int32_t)(link-base)/912;
            ((void (*)(uint32_t,int32_t,uintptr_t))close)((uint8_t)index,index,close);
        }
    }
    (void)opencfw_em9305_associated_reset_32ae50(link);
    uint32_t request=opencfw_em9305_radio_query_3253a4(*(volatile uint16_t *)(link+566u));
    if(request==0u)return opencfw_em9305_auxiliary_signal_304394();
    uintptr_t report=*(volatile uint32_t *)(uintptr_t)0x8052ccu;
    if(report!=0u&&*(volatile uint8_t *)(link+109u)!=0u){
        uint32_t mode=*(volatile uint8_t *)(link+111u);
        if(mode==1u)
            ((void (*)(uint32_t,uint32_t,uintptr_t))report)(*(volatile uint16_t *)(link+262u),0u,report);
        else if(mode==0u)
            ((void (*)(uint32_t,uint32_t,uintptr_t))report)(*(volatile uint32_t *)(link+464u),
                                                           *(volatile uint32_t *)(link+468u),report);
    }
    return opencfw_em9305_radio_request_start_303cd8(request,
        (uint16_t)(*(volatile uint16_t *)(link+566u)+6u));
}
