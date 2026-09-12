/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the command-queue suffix literal pool at
 * 0x00427C80..0x00427C90.
 *
 * The pool closes the retained 30-byte command-queue suffix region
 * (0x00427C72..0x00427C90): its first 14 bytes are the dead tail of
 * the replaced post-loop block-entry body (stock ends with
 * `movs r0, #0; bx lr` at 0x00427C7C/0x00427C7E), and the remaining
 * 16 bytes are this pool. Every slot below names its reviewed
 * spelling from runtime_cmdq_services_427794.c:
 *
 * - 0x200262F0 is OPEN_CFW_CMDQ_STATES (the queue state-table base).
 * - 0x00430880 is OPEN_CFW_CMDQ_REGISTERS (the register-table base).
 * - 0x01CDCDCD is OPEN_CFW_CMDQ_INITIALIZED | OPEN_CFW_CMDQ_MAGIC
 *   (the initialized-prefix word stored by the initializer,
 *   `queue->prefix = (queue->prefix & 0xFC000000U) |
 *   OPEN_CFW_CMDQ_INITIALIZED | OPEN_CFW_CMDQ_MAGIC`).
 * - 0x20080000 is OPEN_CFW_CMDQ_SSRAM_BASE (the shared-RAM base).
 *
 * Loader PCs were verified by anchored per-span Capstone decode of
 * the routed spans plus a sync-independent whole-window encoding
 * sweep for literal-load forms (`ldr [pc]`, `ldr.w [pc]`,
 * `ldrb.w`/`ldrh.w`/`ldrsb.w [pc]`, `adr`/`adr.w`); the sweep is
 * authoritative because anchored Capstone desynchronizes inside the
 * error-resume and post-loop spans and misses two magic loaders
 * (see docs/research/g2-bootloader-bl006-cluster-427c80-42644c-
 * source-closure.md). Every loader sits in a replaced command-queue
 * span whose shipped replacement carries zero data relocations
 * (stale by construction); no loader sits in any byte-exact shipped
 * body, in any retained dead span, or in any relocated source, and
 * no image word anywhere equals any slot address.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Pool at 0x00427C80: queue state-table base, register-table base,
 * initialized-prefix magic, and shared-RAM base. */
struct __attribute__((packed)) open_cfw_bl006_pool_427c80 {
    open_cfw_bl006_u32 state_table_base; /* 0x200262F0:
        OPEN_CFW_CMDQ_STATES (reviewed
        runtime_cmdq_services_427794.c; stale loader in the
        replaced initializer at 0x004277BE). */
    open_cfw_bl006_u32 register_table_base; /* 0x00430880:
        OPEN_CFW_CMDQ_REGISTERS (reviewed
        runtime_cmdq_services_427794.c; stale loader in the
        replaced initializer at 0x00427820). */
    open_cfw_bl006_u32 initialized_prefix; /* 0x01CDCDCD:
        OPEN_CFW_CMDQ_INITIALIZED | OPEN_CFW_CMDQ_MAGIC (reviewed
        runtime_cmdq_services_427794.c prefix store; stale loaders
        in the replaced enable/disable/alloc/release/post/status/
        term/error-resume/post-loop bodies). */
    open_cfw_bl006_u32 ssram_base; /* 0x20080000:
        OPEN_CFW_CMDQ_SSRAM_BASE (reviewed
        runtime_cmdq_services_427794.c; stale loaders in the
        replaced enable/post/post-loop bodies). */
};

__attribute__((used, section(".rodata.bl006_pool_427c80")))
const struct open_cfw_bl006_pool_427c80 open_cfw_bootloader_bl006_pool_427c80 = {
    0x200262F0u, 0x00430880u, 0x01CDCDCDu, 0x20080000u
};
