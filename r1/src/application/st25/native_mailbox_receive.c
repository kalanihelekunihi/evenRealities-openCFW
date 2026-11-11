/* Stock 0x77be0 mailbox gate. Preserve requests while separating receive
 * storage from adjacent IRQ state: an eight-bit length can request 257 bytes. */
#include <stddef.h>
#include <stdint.h>
#include "st25dvxxkc.h"
extern ST25DVxxKC_Object_t r1_st25_device;
extern void r1_st25dvxxkc_dock_frame_policy(uint8_t *,uint32_t,volatile uint8_t *);
_Static_assert(offsetof(ST25DVxxKC_Object_t,Ctx)==28,"selected SDK context");
_Static_assert(sizeof(ST25DVxxKC_EN_STATUS_E)==1,"mailbox mode byte");
uint8_t r1_st25_mailbox_receive_buffer[257]
 __attribute__((section(".bss.r1.st25.mailbox_receive"),aligned(4)))={0};
void r1_st25dvxxkc_bounded_mailbox_receive(volatile uint8_t *output)
{
    ST25DVxxKC_EN_STATUS_E mode=0;
    uint8_t control=0,length=0;
    (void)ST25DVxxKC_ReadMBMode(&r1_st25_device,&mode);
    if (!mode) return;
    /* Stock exposes the raw control byte separately from its decoded struct;
     * the selected SDK exposes that byte through its register API. */
    if (ST25DVxxKC_GetMB_CTRL_DYN_ALL(&r1_st25_device.Ctx,&control)!=0) return;
    if (control!=0x85) return;
    (void)ST25DVxxKC_ReadMBLength_Dyn(&r1_st25_device,&length);
    for (unsigned i=0;i<20;++i) r1_st25_mailbox_receive_buffer[i]=0;
    if (ST25DVxxKC_ReadMailboxData(&r1_st25_device,r1_st25_mailbox_receive_buffer,
                                  0,(uint16_t)length+2u)!=0) return;
    r1_st25dvxxkc_dock_frame_policy(r1_st25_mailbox_receive_buffer,length,output);
}
