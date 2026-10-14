/* Exact Apollo NEMA mode lookups at 0x6df0f4, 0x6df124, 0x513ec0.
 * The two 12-entry format tables are adjacent in native flash. Their valid
 * index domain still needs to be proven before the mode body is admitted.
 */
#include <stdint.h>
const uint32_t display_driver_nema_mode_format_a[12]={
    0x1eu,0x1du,0u,8u,4u,0xcu,5u,0xdu,1u,9u,0x11u,0x15u
};
const uint32_t display_driver_nema_mode_format_b[12]={
    0xfu,0xeu,0u,4u,0u,4u,1u,5u,1u,5u,0xcu,0xcu
};
const uint32_t display_driver_nema_mode_target_bits[4]={
    0x400u,0u,0x800u,0xc00u
};
/* Native indexing can address the four words immediately after format B. */
const uint32_t display_driver_nema_mode_format_b_tail[4]={
    0x6e65735bu,0x5f726f73u,0x5d736c61u,0x20534c41u
};
_Static_assert(sizeof display_driver_nema_mode_format_a==48u,"mode A size");
_Static_assert(sizeof display_driver_nema_mode_format_b==48u,"mode B size");
_Static_assert(sizeof display_driver_nema_mode_target_bits==16u,"target bits size");
_Static_assert(sizeof display_driver_nema_mode_format_b_tail==16u,"format tail size");
