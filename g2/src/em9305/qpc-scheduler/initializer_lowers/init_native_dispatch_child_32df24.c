#include <stdint.h>

/* Native 0x32df24..0x32dfe8: parse an extended advertising header.
 * in[0] gives the header length (bits 0..5) and AdvMode (bits 6..7); a
 * non-empty header has the flags byte in[1] (copied to *flags_out and
 * OR-ed into out[2]) followed by AdvA, TargetA, CTEInfo, ADI, AuxPtr,
 * SyncInfo and TxPower as flagged. AdvA/TargetA go to out+4/+12, CTEInfo
 * to out[20..21], ADI to out+22/24, AuxPtr/SyncInfo pointers to
 * out+32/+36, TxPower to out[25]. Any remaining ACAD is recorded at
 * out+28 with its length+1 at out[26]. Returns the bytes consumed. */
extern uint64_t opencfw_em9305_controller_pack_address(uintptr_t address);

uint32_t opencfw_em9305_dispatch_child_32df24(uintptr_t out, uintptr_t flags_out, uintptr_t in)
{
    volatile uint8_t *o=(volatile uint8_t *)out;
    volatile uint8_t *cursor;
    uint32_t extra=0u;
    *(volatile uint8_t *)flags_out=0u;
    uint32_t first=*(volatile uint8_t *)in;
    o[1]=(uint8_t)(first>>6);
    o[0]=(uint8_t)(first&63u);
    if((first&63u)==0u){
        cursor=(volatile uint8_t *)(in+1u);
    }else{
        uint32_t flags=*(volatile uint8_t *)(in+1u);
        cursor=(volatile uint8_t *)(in+2u);
        *(volatile uint8_t *)flags_out=(uint8_t)flags;
        o[2]=(uint8_t)(o[2]|flags);
        if((flags&1u)!=0u){
            uint64_t address=opencfw_em9305_controller_pack_address((uintptr_t)cursor);
            cursor=(volatile uint8_t *)(in+8u);
            *(volatile uint32_t *)(out+8u)=(uint32_t)(address>>32);
            *(volatile uint32_t *)(out+4u)=(uint32_t)address;
        }
        if((flags&2u)!=0u){
            uint64_t address=opencfw_em9305_controller_pack_address((uintptr_t)cursor);
            cursor+=6;
            *(volatile uint32_t *)(out+16u)=(uint32_t)(address>>32);
            *(volatile uint32_t *)(out+12u)=(uint32_t)address;
        }
        if((flags&4u)!=0u){
            uint32_t cte=*cursor++;
            o[21]=(uint8_t)(cte>>6);
            o[20]=(uint8_t)(cte&31u);
        }
        if((flags&8u)!=0u){
            uint32_t adi=((uint32_t)cursor[1]<<8)+cursor[0];
            cursor+=2;
            *(volatile uint16_t *)(out+22u)=(uint16_t)(adi&0xfffu);
            o[24]=(uint8_t)((adi&0xf000u)>>12);
        }
        if((flags&16u)!=0u){
            *(volatile uint32_t *)(out+32u)=(uint32_t)(uintptr_t)cursor;
            cursor+=3;
        }
        if((flags&32u)!=0u){
            *(volatile uint32_t *)(out+36u)=(uint32_t)(uintptr_t)cursor;
            cursor+=18;
        }
        if((flags&64u)!=0u)o[25]=*cursor++;
    }
    uint32_t length=o[0];
    uint32_t used=(uint32_t)((uintptr_t)cursor-in);
    if(length>=(uint8_t)used){
        extra=length-used+1u;
        *(volatile uint32_t *)(out+28u)=(uint32_t)(uintptr_t)cursor;
        cursor+=extra;
        used=(uint32_t)((uintptr_t)cursor-in);
    }else{
        *(volatile uint32_t *)(out+28u)=0u;
    }
    o[26]=(uint8_t)extra;
    return (uint8_t)used;
}
