/* SPDX-License-Identifier: MIT
 * Stock 0x0800ad48 queue ring insertion. Zero-width mutex release opens
 * the separate task priority inheritance contract at 0x0800cb38.
 */
#include <stdint.h>
extern uint32_t case_kernel_mutex_release(uint32_t task); /* stock 0x0800cb38 */

static void copy_bytes(uint32_t destination,const void *source,uint32_t length)
{
    volatile uint8_t *out=(volatile uint8_t *)(uintptr_t)destination;
    const uint8_t *in=(const uint8_t *)source;
    for(uint32_t i=0;i<length;i++)out[i]=in[i];
}

uint32_t case_queue_copy_in(uint32_t queue,const void *item,uint32_t mode)
{
    volatile uint32_t *q=(volatile uint32_t *)(uintptr_t)queue;
    uint32_t result=0u;
    uint32_t used=q[0x38u/4u];
    uint32_t width=q[0x40u/4u];
    if(width==0u){
        if(q[0]==0u){result=case_kernel_mutex_release(q[2]);q[2]=0u;}
    }else if(mode==0u){
        uint32_t destination=q[1];
        copy_bytes(destination,item,width);
        q[1]=destination+width;
        if(q[2]<=q[1])q[1]=q[0];
    }else{
        uint32_t destination=q[3];
        copy_bytes(destination,item,width);
        q[3]=destination-width;
        if(q[3]<q[0])q[3]=q[2]-width;
        if(mode==2u && used!=0u)used--;
    }
    q[0x38u/4u]=used+1u;
    return result;
}
