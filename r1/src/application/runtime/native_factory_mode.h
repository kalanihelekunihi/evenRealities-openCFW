#ifndef R1_NATIVE_FACTORY_MODE_H
#define R1_NATIVE_FACTORY_MODE_H
#include <stdint.h>
struct factory_state {
    uint8_t active,reserved[7];uint32_t aging,configuration,timer,saved_configuration,acc;
};
extern volatile struct factory_state r1_factory_mode_state;
#endif
