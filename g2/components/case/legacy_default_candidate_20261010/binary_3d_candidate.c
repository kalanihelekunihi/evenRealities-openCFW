/* SPDX-License-Identifier: MIT
 * Isolated stock 0x3d destination-not-2 route, through final lower call.
 */
#include <stdint.h>
extern uint32_t case_binary_3d_control(uint32_t object, uint32_t mask);
extern uint32_t case_binary_3d_logger(const char *format);
extern uint32_t case_binary_3d_dispatch(uint32_t state, const uint8_t *frame, uint32_t length);
uint32_t case_binary_3d_candidate(const uint8_t *command, uint32_t length, uint32_t mode)
{
    if (*(volatile uint8_t *)(uintptr_t)0x200000f5u != 0) {
        case_binary_3d_control(*(volatile uint32_t *)(uintptr_t)0x200000f0u,128);
        if (*(volatile uint8_t *)(uintptr_t)0x200000bfu == 0) {
            case_binary_3d_logger("[AGING_NOT]: exit aging status(0x3D).");
            case_binary_3d_logger("\r\n");
        }
    }
    uint32_t r=mode;
    if (length<5) return r;
    r=command[1];if(r) return r;
    r=command[2];if(r>=2) return r;
    if(mode) {
        r=6u+(uint32_t)command[3]+((uint32_t)command[4]<<8);
        if(r!=length) return r;
        case_binary_3d_control(*(volatile uint32_t *)(uintptr_t)0x200000f0u,1024);
    } else {
        r=5u+(uint32_t)command[3];
        if(r!=length) return r;
        case_binary_3d_control(*(volatile uint32_t *)(uintptr_t)0x200000f0u,32);
    }
    return case_binary_3d_dispatch(0x200001b4u,command,length);
}
