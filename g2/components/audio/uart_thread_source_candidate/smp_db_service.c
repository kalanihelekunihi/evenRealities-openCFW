/* Native SmpDbService 0x542960: ten Cordio records, 1000 ms cadence.
 * The IAR return is the entry R3, saved by its push/pop frame. */
#include <stdint.h>
extern uint8_t audio_ble_smp_database[]; /* 0x200708ec, selected storage */
extern const uint8_t *audio_ble_comm_registration_slot; /* live pSmpCfg cell 0x200004b8 */
extern uint32_t smpDbRecordInUse(const uint8_t *);
extern void smpDbStartServiceTimer(void);
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void wr16(uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static void wr32(uint8_t *p,uint32_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);}
static uint32_t subtract_second(uint32_t value){return value<1001u?0u:value-1000u;}

__attribute__((used,noinline))
void audio_ble_smp_db_service_body(void){
    for(uint32_t i=0u;i<10u;i++){
        uint8_t *record=audio_ble_smp_database+i*0x18u;
        if(smpDbRecordInUse(record)==0u)continue;
        wr32(record+0x10u,subtract_second(rd32(record+0x10u)));
        wr32(record+0x0cu,subtract_second(rd32(record+0x0cu)));
        wr32(record+0x14u,subtract_second(rd32(record+0x14u)));
        if(rd32(record+0x10u)==0u){
            const uint8_t *config=audio_ble_comm_registration_slot;
            uint16_t count=rd16(record+8u),divisor=rd16(config+0x14u);
            count=(uint16_t)(divisor==0u?0u:count/divisor); /* ARM SDIV by zero yields 0 */
            wr16(record+8u,count);
            if(count!=0u)wr32(record+0x10u,rd32(config+0x10u));
        }
        if(rd32(record+0x14u)==0u)record[7u]=0u;
        if(smpDbRecordInUse(record)!=0u)smpDbStartServiceTimer();
    }
}

__attribute__((naked))
uint32_t SmpDbService(void){
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "bl audio_ble_smp_db_service_body\n"
        "pop {r0, r4, r5, pc}\n");
}
