/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the hardware-control SRAM cells at
 * 0x00423E0C..0x00423E14, the MSPI0 base literal at
 * 0x0042499C..0x004249A0, and the MSPI state pool at
 * 0x004251A4..0x004251C0.
 *
 * The control cells are read by the exact source-owned
 * interrupt-atomic hardware-control service; the MSPI words are read
 * by the exact source-owned (AmbiqSuite-equivalent) MSPI services,
 * which keep their stock PC-relative literal addressing, so these
 * pools stay live in the shipped image. Every word below names its
 * value, its live consumers (loader PCs verified by bounded Capstone
 * decode of the routed spans; zero consumers live in entry-redirect
 * stock spans), and its meaning from the already-reviewed consumer
 * host models; see
 * docs/research/g2-bootloader-bl006-cluster-4233e0-4251c0-source-closure.md
 * for the full consumer table.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Pool at 0x00423E0C: interrupt-atomic control-service SRAM cells. */
struct __attribute__((packed)) open_cfw_bl006_pool_423e0c {
    open_cfw_bl006_u32 countdown_cell; /* 0x200271C2: retry-countdown
        cell (control critical service, 0x00423DF2); host model
        `open_cfw_hwcs_host_countdown`, decremented under primask. */
    open_cfw_bl006_u32 latch_cell; /* 0x200271C3: completion-latch cell
        (control critical service, 0x00423DD8); host model
        `open_cfw_hwcs_host_latch`, cleared when the countdown
        expires. */
};

__attribute__((used, section(".rodata.bl006_pool_423e0c")))
const struct open_cfw_bl006_pool_423e0c open_cfw_bootloader_bl006_pool_423e0c = {
    0x200271C2u, 0x200271C3u
};

/* Word at 0x0042499C: MSPI0 register base, 0x1000 stride per module.
 * Read by the MSPI device-configuration service (0x004241AA/
 * 0x004241F2), FIFO read (0x00423EC2/0x00423EE6), and FIFO write
 * (0x00423E5A); the AmbiqSuite-equivalent sources spell it
 * `0x40060000U + module * 0x1000U`. */
__attribute__((used, section(".rodata.bl006_word_42499c")))
const open_cfw_bl006_u32 open_cfw_bootloader_bl006_word_42499c = 0x40060000u;

/* Pool at 0x004251A4: MSPI controller state and control words. */
struct __attribute__((packed)) open_cfw_bl006_pool_4251a4 {
    open_cfw_bl006_u32 register_base; /* 0x40060000: MSPI register base
        (device-configure-public 0x00424CA8/0x00424D9E/0x00424DBE/
        0x00424E74, disable 0x0042514C, enable 0x004250A4,
        PIO-mixed configure 0x004248C6/0x004248DA, sequence loopback
        0x0042498E); module stride 0x1000. */
    open_cfw_bl006_u32 clock_gate_reg; /* 0x40004110: clock-gate
        register read-modified-written by the MSPI clock-generator
        control service (0x004249BC/0x004249DE/0x004249FA). */
    open_cfw_bl006_u32 init_state_base; /* 0x2001CAA0: MSPI init
        state-table base (configure 0x00424B42, initialize 0x00424A70);
        host model `0x2001CAA0U + module * STATE_BYTES`. */
    open_cfw_bl006_u32 handle_prefix; /* 0x01BEBEBE: initialized-handle
        prefix sentinel, low 25 bits (configure 0x00424B00,
        deinitialize 0x0042517A, device-configure-public 0x00424BF6,
        disable 0x00425100, enable 0x00425074); host models spell it
        `(prefix & 0x01FFFFFFU) == 0x01BEBEBEU`. */
    open_cfw_bl006_u32 tcb_ssram_limit; /* 0x20080000: transfer-block
        SSRAM limit (configure 0x00424B68); host model
        `end < 0x20080000U ? 1U : 0U` selects the SRAM-resident flag. */
    open_cfw_bl006_u32 reserved_word; /* 0xFC001F03: reserved word with
        no routed consumer (verified: no PC-relative loader in any
        routed span, live or entry-redirect stock). Reproduced as a
        named constant preserving layout, not as claimed data; if a
        future consumer is found this field must be re-derived. */
    open_cfw_bl006_u32 cq_setclear; /* 0x00400080: command-queue
        set/clear word (enable 0x004250A0); host model
        `store32(registers + 0x2B4U, 0x00400080U)` and
        `trace->cq_setclear = 0x00400080U`. */
};

__attribute__((used, section(".rodata.bl006_pool_4251a4")))
const struct open_cfw_bl006_pool_4251a4 open_cfw_bootloader_bl006_pool_4251a4 = {
    0x40060000u, 0x40004110u, 0x2001CAA0u, 0x01BEBEBEu, 0x20080000u,
    0xFC001F03u, 0x00400080u
};
