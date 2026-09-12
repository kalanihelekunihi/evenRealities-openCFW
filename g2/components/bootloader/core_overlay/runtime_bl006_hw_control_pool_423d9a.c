/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the hardware-control register literal at
 * 0x00423D9A..0x00423DA0 and the two-byte alignment at
 * 0x00423DCE..0x00423DD0.
 *
 * Both sit between byte-exact source-owned in-place leaves (the global
 * hardware-control service, register query, indexed test, zero-index
 * wrapper, and interrupt-atomic control service in
 * runtime_hw_control_services_423d20.c), which keep their stock
 * PC-relative literal addressing, so the literal stays live in the
 * shipped image. Every word below names its value, its exact-body
 * consumers (loader PCs verified by bounded Capstone decode of the
 * routed spans; zero consumers live in entry-redirect stock spans),
 * and its meaning from the already-reviewed consumer host model; see
 * docs/research/g2-bootloader-bl006-cluster-423d9a-426c10-source-closure.md
 * for the full consumer table.
 */

typedef __UINT16_TYPE__ open_cfw_bl006_u16;
typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Pool at 0x00423D9A: 2-byte alignment fill plus the control-register
 * address. The register query (0x00423D82) and the global service
 * (0x00423D28/0x00423D3E) load this word as the register argument of
 * `open_cfw_hwcs_host_register_call(1000U, 0xE0000E80U, ...)`; the
 * query passes mask 0x00800000U, the global service passes 0U. */
struct __attribute__((packed)) open_cfw_bl006_pool_423d9a {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment; the
        register query body ends at 0x00423D9A */
    open_cfw_bl006_u32 control_register; /* 0xE0000E80: hardware-control
        register address under test */
};

__attribute__((used, section(".rodata.bl006_pool_423d9a")))
const struct open_cfw_bl006_pool_423d9a open_cfw_bootloader_bl006_pool_423d9a = {
    0x0000u, 0xE0000E80u
};

/* Alignment at 0x00423DCE: 0x0000 pads the zero-index test wrapper
 * (ends 0x00423DCE) so the interrupt-atomic control-service entry at
 * 0x00423DD0 is word-aligned. */
__attribute__((used, section(".rodata.bl006_align_423dce")))
const open_cfw_bl006_u16 open_cfw_bootloader_bl006_align_423dce = 0x0000u;
