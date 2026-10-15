/* Apollo S200 Hongshi register-read descriptor at 0x5bbe3e. */
#include <stdint.h>

extern uint32_t display_driver_uled_type0_packet_59cc40(void *);

uint32_t display_driver_uled_type1_read_register_5bbe3e(
        uint32_t bank,uint32_t *output,uint32_t count,uint32_t mode) {
    uint8_t descriptor[28];
    const uint8_t *template=(const uint8_t *)(uintptr_t)0x76b148u;
    for (uint32_t i=0;i<28u;i++) descriptor[i]=template[i];
    uint32_t command=(bank&0xffu)|((mode==1u?0x7bu:0x79u)<<8);
    uint32_t words[4]={command,count,(uint32_t)(uintptr_t)output,
        *(volatile const uint32_t *)(uintptr_t)0x20074510u};
    const uint32_t offsets[4]={4u,12u,20u,24u};
    for (uint32_t j=0;j<4u;j++)
        for (uint32_t i=0;i<4u;i++)
            descriptor[offsets[j]+i]=(uint8_t)(words[j]>>(8u*i));
    return display_driver_uled_type0_packet_59cc40(descriptor);
}
