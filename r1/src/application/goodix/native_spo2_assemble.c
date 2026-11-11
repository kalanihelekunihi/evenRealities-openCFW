#include <stdint.h>
#include <stddef.h>
extern uint32_t r1_goodix_version_qualifier(char *);
extern void r1_goodix_spo2_decode(const void *,uint32_t,uint32_t,void *);
static uint32_t word(uintptr_t p,uint32_t offset)
{return *(const volatile uint32_t *)(p+offset);}
static uint8_t byte(uintptr_t p,uint32_t offset)
{return *(const volatile uint8_t *)(p+offset);}
static void put(uintptr_t p,uint32_t offset,uint32_t value)
{*(volatile uint32_t *)(p+offset)=value;}
uint32_t r1_goodix_spo2_integrity_encode(uint32_t value)
{
    const uint32_t masks[4]={0x6b851eb7u,0x4147ae13u,0x28f5c28fu,0x15c28f5bu};
    uint32_t reduced=((value&0xffffffu)>>1)^masks[(value&7u)>>1];
    uint32_t parity=0;
    while(reduced){parity^=1u;reduced&=reduced-1u;}
    return (value&0xfffffffeu)|parity;
}
uint32_t r1_goodix_spo2_integrity_check(uint32_t value)
{return r1_goodix_spo2_integrity_encode(value)!=value;}
uint32_t r1_goodix_spo2_assemble(const void *input,uint32_t sequence,const void *descriptor,void *output)
{
    uintptr_t raw=(uintptr_t)input,desc=(uintptr_t)descriptor,out=(uintptr_t)output;
    if(r1_goodix_version_qualifier(NULL)){
        uint32_t count=(uint32_t)byte(raw,4)*3u;
        for(uint32_t i=0;i<count;++i){
            if(byte(word(raw,8),i)){
                uint32_t value=word(word(raw,12),i*4u);
                if(r1_goodix_spo2_integrity_check(value)==1)put(word(raw,12),i*4u,0x800000u);
            }
        }
    }
    put(out,0,sequence-1u);
    put(out,12,word(raw,24));put(out,16,word(raw,28));put(out,20,word(raw,32));
    uint32_t count=byte(raw,4);uint8_t records=0;
    for(uint32_t i=0;i<count;++i){
        for(uint32_t group=0;group<3;++group){
            uint32_t index=i+count*group;
            if((byte(word(raw,8),index/8u)>>(7u-index%8u))&1u){
                if(records<word(desc,0))
                    r1_goodix_spo2_decode(input,i,group,(void *)((uintptr_t)word(out,8)+(uint32_t)records*24u+group*8u));
                if(group==2){
                    ++records;
                    *(volatile uint8_t *)(out+4)=(uint8_t)(byte(out,4)+1u);
                }
            }
        }
    }
    return word(desc,0)!=(uint32_t)records;
}
