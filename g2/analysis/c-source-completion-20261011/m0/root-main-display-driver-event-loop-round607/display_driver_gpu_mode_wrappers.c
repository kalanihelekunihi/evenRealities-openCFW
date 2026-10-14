/* Apollo Ambiq mode wrappers 0x4b0730 and 0x4b0748. Candidate. */
#include <stdint.h>
extern void display_driver_gpu_mode_lower_4b06c0(uint32_t,uint32_t,uint32_t,
                                                  uint32_t,uint32_t,uint32_t);
void display_driver_gpu_mode_4b0730(uint32_t unit,uint32_t enabled) {
    display_driver_gpu_mode_lower_4b06c0(unit,enabled,0u,UINT32_MAX,UINT32_MAX,0u);
}
void display_driver_gpu_enable_4b0748(uint32_t unit,uint32_t enabled) {
    display_driver_gpu_mode_lower_4b06c0(unit,enabled,0u,1u,UINT32_MAX,0u);
}
