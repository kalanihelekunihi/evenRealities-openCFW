/* Candidate uLED driver workspace, native pointer 0x203795a0.
 * The next decoded absolute SRAM pointer is 0x203799a0, 0x400 bytes later.
 * This supports a non-overlapping provisional allocation, not an exact
 * ownership or linker-placement proof.
 */
#include <stdint.h>

__attribute__((aligned(32))) uint8_t display_driver_uled_work_buffer[0x400];
_Static_assert(sizeof display_driver_uled_work_buffer == 0x400u,
               "provisional uLED workspace span");
