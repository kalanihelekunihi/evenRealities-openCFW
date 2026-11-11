#ifndef R1_NATIVE_GOMORE_ACCEL_AXIS_GATE_H
#define R1_NATIVE_GOMORE_ACCEL_AXIS_GATE_H
#include <stdint.h>
/* Stock 0x582c4: raw three-axis history ranking and signed-byte count gate. */
uint32_t r1_gomore_accel_axis_gate_native(uint32_t,uint32_t,uint32_t,uint32_t,
                                        uint32_t,uint32_t,uint32_t,uint32_t);
#endif
