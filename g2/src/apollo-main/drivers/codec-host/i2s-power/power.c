#include <stdint.h>
/* 0x590648 am_hal_i2s_power_control and 0x5900ce am_hal_i2s_deinitialize were
 * retired here in favour of the upstream AmbiqSuite 5.1.0 am_hal_i2s.c unit;
 * audio_i2s_power_selected / audio_i2s_uninitialize_selected are payload
 * defsym aliases of the upstream functions. */
/* Optional platform control callback at table+4; NULL is an actual no-op provider branch. */
uint32_t audio_power_control_dispatch(uint32_t action,uint32_t enable,void *metadata){
 uint32_t (*callback)(uint8_t,uint8_t,void*)=*(void**)0x20073274u;
 return callback?callback((uint8_t)action,(uint8_t)enable,metadata):0;
}
