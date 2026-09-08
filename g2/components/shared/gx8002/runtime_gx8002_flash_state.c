/* SPDX-License-Identifier: MIT */
/* Recovered initial 32-byte state at runtime 0x200264e4. Discovery owns
 * index/size/address width/device. OTP routines use the command scratch
 * bytes. Initialization installs the final two transfer callbacks. */
#include "runtime_gx8002_flash_state.h"
volatile struct open_cfw_gx8002_flash_state_layout open_cfw_gx8002_flash_state = {
    .device_index = -1,
};
