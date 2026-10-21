/* SPDX-License-Identifier: MIT
 * Scalar Apollo510 MSPI command-queue peripheral resources reconstructed
 * byte-for-byte from ota_s200_bootloader.bin at load address 0x430880.
 */
#include <stdint.h>

typedef struct {
    uint32_t option_register;
    uint32_t buffer_register;
    uint32_t reset_register_a;
    uint32_t reset_register_b;
    uint32_t control_register;
    uint32_t control_mask;
    uint32_t status_register;
    uint32_t option_value;
    uint32_t reset_value;
    uint32_t control_value;
} opencfw_bl_cmdq_resource_t;

/* All pointer-shaped fields are MMIO addresses in 0x400xxxxx. The remaining
 * four words per row are scalar masks/values. There are no code/data pointers
 * or callback fields in this table. */
__attribute__((section(".cmdq_resources"), used, aligned(4)))
const opencfw_bl_cmdq_resource_t opencfw_bl_cmdq_resources[12] = {
    {0x40050228u,0x4005022cu,0x40050240u,0x40050244u,0x4005023cu,0x00008000u,0x40050230u,1u,4u,2u},
    {0x40051228u,0x4005122cu,0x40051240u,0x40051244u,0x4005123cu,0x00008000u,0x40051230u,1u,4u,2u},
    {0x40052228u,0x4005222cu,0x40052240u,0x40052244u,0x4005223cu,0x00008000u,0x40052230u,1u,4u,2u},
    {0x40053228u,0x4005322cu,0x40053240u,0x40053244u,0x4005323cu,0x00008000u,0x40053230u,1u,4u,2u},
    {0x40054228u,0x4005422cu,0x40054240u,0x40054244u,0x4005423cu,0x00008000u,0x40054230u,1u,4u,2u},
    {0x40055228u,0x4005522cu,0x40055240u,0x40055244u,0x4005523cu,0x00008000u,0x40055230u,1u,4u,2u},
    {0x40056228u,0x4005622cu,0x40056240u,0x40056244u,0x4005623cu,0x00008000u,0x40056230u,1u,4u,2u},
    {0x40057228u,0x4005722cu,0x40057240u,0x40057244u,0x4005723cu,0x00008000u,0x40057230u,1u,4u,2u},
    {0x400602a0u,0x400602a8u,0x400602c0u,0x400602c4u,0x400602b8u,0x00004000u,0x400602acu,1u,4u,8u},
    {0x400612a0u,0x400612a8u,0x400612c0u,0x400612c4u,0x400612b8u,0x00004000u,0x400612acu,1u,4u,8u},
    {0x400622a0u,0x400622a8u,0x400622c0u,0x400622c4u,0x400622b8u,0x00004000u,0x400622acu,1u,4u,8u},
    {0x400632a0u,0x400632a8u,0x400632c0u,0x400632c4u,0x400632b8u,0x00004000u,0x400632acu,1u,4u,8u},
};

_Static_assert(sizeof(opencfw_bl_cmdq_resource_t) == 40,
               "CMDQ resource row must be 40 bytes");
