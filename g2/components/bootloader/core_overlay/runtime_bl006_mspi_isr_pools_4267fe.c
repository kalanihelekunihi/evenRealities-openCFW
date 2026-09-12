/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: the MSPI interrupt-service literal pool at
 * 0x004267FE..0x00426808 and the power-control literal pool at
 * 0x00426BFE..0x00426C10.
 *
 * Each pool holds one 2-byte alignment fill plus 32-bit words named
 * below. Words consumed by the byte-exact interrupt-service and
 * power-control bodies (reviewable Thumb-2 in
 * runtime_mspi_interrupt_power_426536.S, installed in place) keep
 * their stock PC-relative literal addressing and stay live in the
 * shipped image; their loader PCs are verified by bounded Capstone
 * decode of the routed spans. The two callback-pointer words
 * (0x00424979/0x00424977) are a documented weaker case: their values
 * are live in the shipped image -- the production AmbiqSuite control
 * body spells them and stores them into the command-queue callback
 * table (runtime_mspi_control_4251c0.c), and their targets are the
 * exact source-owned seq_loopback/dummy_callback bodies -- but no
 * byte-exact shipped body loads these two slots (the only stock-decode
 * loaders sit inside the functionally replaced control span, whose
 * shipped bytes differ, so those hits are stale, not live). They are
 * reproduced as named layout-preserving fields, not as claimed live
 * data; if a future exact body loads either slot, its field comment
 * must be re-derived. See
 * docs/research/g2-bootloader-bl006-cluster-423d9a-426c10-source-closure.md
 * for the full consumer table, including the relocation-contract
 * argument (zero non-call relocations in every functional consumer)
 * behind the stale-loader classification.
 */

typedef __UINT16_TYPE__ open_cfw_bl006_u16;
typedef __UINT32_TYPE__ open_cfw_bl006_u32;

/* Pool at 0x004267FE: alignment, the sequence-loopback callback
 * pointer, and the MSPI register base. */
struct __attribute__((packed)) open_cfw_bl006_pool_4267fe {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment */
    open_cfw_bl006_u32 seq_loopback_ptr; /* 0x00424979: Thumb pointer
        to the exact source-owned mspi_seq_loopback callback body at
        [0x00424978,0x0042499C). The shipped control body stores this
        value into pfnCallback[] on the loop path
        (runtime_mspi_control_4251c0.c); no byte-exact shipped body
        loads this slot -- value-live, slot-load unproven (see
        header). */
    open_cfw_bl006_u32 register_base; /* 0x40060000: MSPI register
        base, 0x1000 module stride. Loaded by the exact
        interrupt-service body (0x0042656E/0x00426762/0x004267CC)
        as `base + module << 12`; AmbiqSuite-equivalent sources
        spell `0x40060000U + module * 0x1000U`. */
};

__attribute__((used, section(".rodata.bl006_pool_4267fe")))
const struct open_cfw_bl006_pool_4267fe open_cfw_bootloader_bl006_pool_4267fe = {
    0x0000u, 0x00424979u, 0x40060000u
};

/* Pool at 0x00426BFE: alignment, the dummy-callback pointer, the
 * handle prefix, the state-table base, and the MSPI register base. */
struct __attribute__((packed)) open_cfw_bl006_pool_426bfe {
    open_cfw_bl006_u16 align_fill; /* 0x0000: pool alignment */
    open_cfw_bl006_u32 dummy_callback_ptr; /* 0x00424977: Thumb
        pointer to the exact source-owned mspi_dummy_callback
        (`bx lr`) body at [0x00424976,0x00424978). The shipped
        control body stores this value into pfnCallback[] on the
        dummy-callback path (runtime_mspi_control_4251c0.c); no
        byte-exact shipped body loads this slot -- value-live,
        slot-load unproven (see header). */
    open_cfw_bl006_u32 handle_prefix; /* 0x01BEBEBE:
        initialized-handle prefix sentinel, low 25 bits. The exact
        interrupt-service body (0x00426548) compares
        `(handle & ~0xFE000000U)` against it, as does the exact
        power-control body (0x0042681A); host models spell
        `(prefix & 0x01FFFFFFU) == 0x01BEBEBEU`. */
    open_cfw_bl006_u32 init_state_base; /* 0x2001CAA0: MSPI init
        state-table base. The exact interrupt-service body
        (0x0042667E) derives `base + module * 0x8D0U + 0x828U` on
        the command-queue path; host model
        `0x2001CAA0U + module * STATE_BYTES`. */
    open_cfw_bl006_u32 register_base; /* 0x40060000: MSPI register
        base, 0x1000 module stride. Loaded by the exact
        power-control body (0x0042688A/0x00426A40/0x00426BBC) as
        `base + module << 12`. */
};

__attribute__((used, section(".rodata.bl006_pool_426bfe")))
const struct open_cfw_bl006_pool_426bfe open_cfw_bootloader_bl006_pool_426bfe = {
    0x0000u, 0x00424977u, 0x01BEBEBEu, 0x2001CAA0u, 0x40060000u
};
