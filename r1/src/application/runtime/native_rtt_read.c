/* Native 0x31964/0x3194c and pinned SEGGER RTT receive-ring semantics.
 * Reuse the source-owned native initializer and SDK control block; retaining
 * the SDK's full read graph would also retain its separate default buffers. */
#include <stdint.h>
#include <string.h>
#include "SEGGER_RTT.h"
unsigned SEGGER_RTT_ReadNoLock(unsigned channel,void *destination,unsigned capacity)
{
    if (_SEGGER_RTT.acID[0]!='S') SEGGER_RTT_Init();
    SEGGER_RTT_BUFFER_DOWN *ring=&_SEGGER_RTT.aDown[channel];
    unsigned write=ring->WrOff,read=ring->RdOff,total=0;
    unsigned char *out=destination;
    if(read>write){
        unsigned count=ring->SizeOfBuffer-read;
        if(count>capacity)count=capacity;
        memcpy(out,ring->pBuffer+read,count);
        total+=count;read+=count;
        if(read==ring->SizeOfBuffer)read=0;
        capacity-=count;out+=count;
    }
    unsigned count=write-read;
    if(count>capacity)count=capacity;
    if(count){
        memcpy(out,ring->pBuffer+read,count);
        total+=count;read+=count;
    }
    if(total)ring->RdOff=read;
    return total;
}
unsigned SEGGER_RTT_Read(unsigned channel,void *destination,unsigned capacity)
{
    uint32_t previous=__builtin_arm_rsr("basepri");
    __builtin_arm_wsr("basepri",32);
    unsigned count=SEGGER_RTT_ReadNoLock(channel,destination,capacity);
    __builtin_arm_wsr("basepri",(uint8_t)previous);
    return count;
}
