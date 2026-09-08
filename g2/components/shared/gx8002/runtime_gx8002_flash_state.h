/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_FLASH_STATE_H
#define OPEN_CFW_GX8002_FLASH_STATE_H
#include <stdint.h>
#include <stddef.h>
struct open_cfw_gx8002_flash_state_layout {
    int32_t device_index;
    uint32_t usable_bytes;
    uint32_t address_bytes;
    uintptr_t selected_device;
    uint8_t command[8];
    int (*program_words)(unsigned, const uint32_t *, unsigned);
    int (*read_words)(unsigned, uint32_t *, unsigned);
};
extern volatile struct open_cfw_gx8002_flash_state_layout open_cfw_gx8002_flash_state;
_Static_assert(sizeof(struct open_cfw_gx8002_flash_state_layout)==32,"state size");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_state_layout,command)==16,"command offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_state_layout,program_words)==24,"program offset");
_Static_assert(offsetof(struct open_cfw_gx8002_flash_state_layout,read_words)==28,"read offset");

#endif
