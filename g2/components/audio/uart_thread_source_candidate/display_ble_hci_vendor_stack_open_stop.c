/* Native vendor stack open 0x55c2bc and stop 0x55c430.
 * ROM slots 0x55cc18 -> live rows 0x2003b558, 0x55c548 -> 0x40050000;
 * constants 0x01123456/0x00123456 are authenticated at 0x55cc14/cf30. */
#include <stdint.h>
extern uint8_t audio_ble_vendor_stack_rows_2003b558[]; /* eight 0x8a8-byte rows */
extern uint32_t audio_ble_vendor_stack_stop_hal_55c11a(uint8_t *row);
static uint32_t get32(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put32(uint8_t *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}

uint32_t audio_ble_radio_stack_open_55c2bc(uint32_t index,void *out) {
    if(index>=8u)return 5u;
    if(out==0)return 6u;
    uint8_t *row=audio_ble_vendor_stack_rows_2003b558+index*0x8a8u;
    uint32_t flags=get32(row);
    if((flags&0x01000000u)!=0u)return 7u;
    flags=(flags|0x01000000u)&~0x02000000u;
    flags=(flags&0xff000000u)|0x00123456u;
    put32(row,flags);put32(row+4u,index);
    put32((uint8_t *)out,(uint32_t)(uintptr_t)row);
    return 0u;
}

uint32_t audio_ble_hci_radio_stack_stop_55c430(uint32_t pointer) {
    uint8_t *row=(uint8_t *)(uintptr_t)pointer;
    if(row==0||(get32(row)&0x01ffffffu)!=0x01123456u)return 2u;
    uint32_t flags=get32(row);
    if((flags&0x02000000u)==0u)return 0u;
    if(get32(row+0x24u)!=0u)return 3u;
    uint32_t index=get32(row+4u);
    volatile uint32_t *reg=(volatile uint32_t *)(uintptr_t)(0x40050000u+index*0x1000u+0x11cu);
    *reg&=~1u;
    *reg&=~0x10u;
    (void)audio_ble_vendor_stack_stop_hal_55c11a(row);
    put32(row,flags&~0x02000000u);
    return 0u;
}
