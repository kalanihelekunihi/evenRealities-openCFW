/* SPDX-License-Identifier: MIT. Reconstructed scalar ROM data used by mode1.
 * These are register IDs/values, not stock executable bytes. Fixed placement
 * supports the bounded comparison; it is not a complete firmware layout.
 */
#include <stdint.h>
__attribute__((section(".boot_runtime_ids"), used))
const uint32_t opencfw_boot_mode_one_register_ids[2] = {12u, 14u};
__attribute__((section(".boot_runtime_values"), used))
const uint32_t opencfw_boot_mode_values[2] = {3u, 0xe083u};
