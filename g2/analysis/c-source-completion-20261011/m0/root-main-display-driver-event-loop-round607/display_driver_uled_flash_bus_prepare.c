/* Apollo 0x4c3500: flash/display pin group preparation. Pin IDs and
 * fallthrough groups are instruction-backed; 0x78ee48 is ROM pin data.
 */
#include <stdint.h>

extern uint32_t g2_codec_pin_function(uint32_t,uint32_t);

static uint32_t prepare_pin(uint32_t pin_id) {
    uint32_t configuration=*(volatile const uint32_t *)(uintptr_t)0x78ee48u;
    return g2_codec_pin_function(pin_id,configuration);
}

uint32_t display_driver_uled_flash_bus_prepare_4c3500(uint32_t mode,
                                                        uint32_t option) {
    uint8_t choice=(uint8_t)option;
    uint32_t result=mode;
    if (mode==0u) {
        if (choice==10u) {
            for (uint32_t pin=0x25u;pin<=0x2du;++pin) result=prepare_pin(pin);
        } else if (choice!=0u && choice!=4u && choice!=6u && choice!=8u &&
                   choice!=16u && choice!=18u) return result;
        if (choice==10u || choice==6u || choice==8u)
            for (uint32_t pin=0x44u;pin<=0x47u;++pin) result=prepare_pin(pin);
        if (choice==10u || choice==6u || choice==8u || choice==4u ||
            choice==16u || choice==18u)
            for (uint32_t pin=0x42u;pin<=0x43u;++pin) result=prepare_pin(pin);
        static const uint8_t base_pins[]={0xc7u,0x40u,0x41u,0x48u,0x49u};
        for (uint32_t i=0;i<sizeof base_pins;++i) result=prepare_pin(base_pins[i]);
        return result;
    }
    if (mode==1u) {
        if (choice!=0u && choice!=4u && choice!=6u && choice!=8u &&
            choice!=16u && choice!=18u) return result;
        if (choice==6u || choice==8u)
            for (uint32_t pin=0x63u;pin<=0x66u;++pin) result=prepare_pin(pin);
        if (choice==4u || choice==6u || choice==8u || choice==16u || choice==18u)
            for (uint32_t pin=0x61u;pin<=0x62u;++pin) result=prepare_pin(pin);
        static const uint8_t base_pins[]={0x31u,0x5fu,0x60u,0x67u,0x68u};
        for (uint32_t i=0;i<sizeof base_pins;++i) result=prepare_pin(base_pins[i]);
    }
    return result;
}
