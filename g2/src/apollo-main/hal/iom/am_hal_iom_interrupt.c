/* AmbiqSuite IOM HAL interrupt group, stock mcu/apollo510/hal/mcu/am_hal_iom.c
 * (pre-SDK-5.2 drop). Native 0x55c174..0x55c1df and 0x55c498..0x55c7df; literal
 * pool words 0x55c548 (IOM0 base 0x40050000), 0x55cc14 (handle magic
 * 0x01123456), 0x55cf38 (IOM0 base) and 0x55cf3c (~(DCMP|CMDCMP)).
 *
 * The behaviour of these five functions is text-equivalent to the pinned
 * AmbiqSuite 5.1.0 am_hal_iom.c (no FDNB dispatch in the service routine).
 * The rest of the island is reconstructed elsewhere under older names, so the
 * upstream file cannot be compiled alongside it; these are hand-written. */
#include <stdint.h>
#include <stddef.h>

#define IOM_BASE        0x40050000u
#define IOM_STRIDE      0x1000u
#define IOM_HANDLE_MAGIC 0x01123456u

/* IOMn register offsets used here. */
#define IOM_CMD         0x120u
#define IOM_OFFSETHI    0x128u
#define IOM_INTEN       0x200u
#define IOM_INTSTAT     0x204u
#define IOM_INTCLR      0x208u
#define IOM_DMACFG      0x218u
#define IOM_DMATOTCOUNT 0x21cu
#define IOM_DMATARGADDR 0x220u
#define IOM_DMASTAT     0x224u
#define IOM_CQCFG       0x228u
#define IOM_CQSETCLEAR  0x238u
#define IOM_DEVCFG      0x2c4u

#define IOM_INT_THR     0x00000002u
#define IOM_INT_CMDCMP_DERR 0x00000801u /* CMDCMP | DERR */
#define IOM_INT_DCMP_ERR    0x00004e7cu /* DCMP | ERR */
#define IOM_INT_ERR         0x00004a7cu
#define IOM_SC_UNPAUSE_CQ   0x00800000u

#define IOM_REG(module, off) \
    (*(volatile uint32_t *)(uintptr_t)(IOM_BASE + (module) * IOM_STRIDE + (off)))

typedef void (*iom_callback_t)(void *ctxt, uint32_t status);

/* High-priority (DMA) queue entry, 32 bytes. */
typedef struct {
    uint32_t offsethi;    /* +0x00 */
    uint32_t devcfg;      /* +0x04 */
    uint32_t dmatotcount; /* +0x08 */
    uint32_t dmatargaddr; /* +0x0c */
    uint32_t dmacfg;      /* +0x10 */
    uint32_t cmd;         /* +0x14 */
    iom_callback_t callback; /* +0x18 */
    void *callback_ctxt;  /* +0x1c */
} g2_iom_dma_entry_t;
_Static_assert(sizeof(g2_iom_dma_entry_t) == 0x20, "IOM HP entry is 32 bytes");

/* am_hal_iom_state_t prefix used by the interrupt path. */
typedef struct {
    uint32_t prefix;              /* +0x000 magic | init(bit24) | enable(bit25) */
    uint32_t module;              /* +0x004 */
    uint8_t pad_008[0x014 - 0x008];
    uint32_t user_int_cfg;        /* +0x014 */
    uint32_t txn_int;             /* +0x018 accumulated INTSTAT (HP) */
    uint32_t last_idx_processed;  /* +0x01c */
    uint32_t pad_020;             /* +0x020 */
    uint32_t num_pend;            /* +0x024 */
    iom_callback_t callback[256]; /* +0x028 */
    void *callback_ctxt[256];     /* +0x428 */
    uint32_t cmdq;                /* +0x828 am_hal_cmdq handle */
    uint8_t seq;                  /* +0x82c 2 = sequence running */
    uint8_t pad_82d[0x834 - 0x82d];
    uint8_t restart;              /* +0x834 */
    uint8_t pad_835[0x83c - 0x835];
    uint8_t hp;                   /* +0x83c high-priority DMA active */
    uint8_t pad_83d[0x840 - 0x83d];
    uint32_t num_hp;              /* +0x840 */
    uint32_t pad_844;             /* +0x844 */
    uint32_t max_hp;              /* +0x848 */
    uint32_t pad_84c;             /* +0x84c */
    uint32_t last_hp_idx;         /* +0x850 */
    g2_iom_dma_entry_t *hp_txn;   /* +0x854 */
} g2_iom_state_t;
_Static_assert(offsetof(g2_iom_state_t, callback_ctxt) == 0x428, "ctxt offset");
_Static_assert(offsetof(g2_iom_state_t, cmdq) == 0x828, "cmdq offset");
_Static_assert(offsetof(g2_iom_state_t, hp) == 0x83c, "bHP offset");
_Static_assert(offsetof(g2_iom_state_t, hp_txn) == 0x854, "HP array offset");

/* Island helpers reconstructed under their earlier names. */
extern int32_t audio_ble_vendor_finish_55bd70(uint32_t module, uint32_t int_status); /* internal_iom_get_int_err */
extern void audio_ble_vendor_recover_55bdac(uint8_t *state, uint32_t int_status);   /* internal_iom_reset_on_error */
extern void audio_ble_vendor_option_before_store_55c13a(void *state);               /* am_hal_iom_CQEnable */
extern void audio_ble_vendor_option_after_load_55c168(void *state);                 /* am_hal_iom_CQDisable */
extern uint32_t display_driver_uled_mspi_queue_snapshot_53901a(uint32_t cmdq, uint32_t *status); /* am_hal_cmdq_get_status */
extern uint32_t display_driver_uled_mspi_queue_release_5390fc(uint32_t cmdq);       /* am_hal_cmdq_error_resume */

static int iom_handle_ok(const g2_iom_state_t *s)
{
    return s != NULL && (s->prefix & 0x01ffffffu) == IOM_HANDLE_MAGIC;
}

/* program_dma: post the next high-priority entry (index last_hp_idx + 1). */
void am_hal_iom_program_dma_55c174(g2_iom_state_t *s)
{
    uint32_t module = s->module;
    const g2_iom_dma_entry_t *e = &s->hp_txn[(s->last_hp_idx + 1u) % s->max_hp];

    IOM_REG(module, IOM_OFFSETHI) = e->offsethi;
    IOM_REG(module, IOM_DEVCFG) = e->devcfg;
    IOM_REG(module, IOM_DMACFG) = 0u;
    IOM_REG(module, IOM_DMATOTCOUNT) = e->dmatotcount;
    IOM_REG(module, IOM_DMATARGADDR) = e->dmatargaddr;
    IOM_REG(module, IOM_DMACFG) = e->dmacfg;
    IOM_REG(module, IOM_CMD) = e->cmd;
}

uint32_t am_hal_iom_interrupt_enable_55c498(void *handle, uint32_t mask)
{
    g2_iom_state_t *s = handle;
    if (!iom_handle_ok(s))
        return 2u;
    if (mask & IOM_INT_THR)
        return 6u; /* threshold interrupt must not be used */
    IOM_REG(s->module, IOM_INTEN) |= mask;
    return 0u;
}

uint32_t am_hal_iom_interrupt_status_get_55c4d0(void *handle, uint8_t enabled_only, uint32_t *status)
{
    g2_iom_state_t *s = handle;
    if (!iom_handle_ok(s))
        return 2u;
    if (status == NULL)
        return 6u;
    uint32_t module = s->module;
    uint32_t v = IOM_REG(module, IOM_INTSTAT);
    if (enabled_only)
        v &= IOM_REG(module, IOM_INTEN);
    *status = v;
    return 0u;
}

uint32_t am_hal_iom_interrupt_clear_55c518(void *handle, uint32_t mask)
{
    g2_iom_state_t *s = handle;
    if (!iom_handle_ok(s))
        return 2u;
    uint32_t module = s->module;
    IOM_REG(module, IOM_INTCLR) = mask;
    (void)IOM_REG(module, IOM_INTSTAT); /* read back to flush the write */
    return 0u;
}

uint32_t am_hal_iom_interrupt_service_55c558(void *handle, uint32_t mask)
{
    g2_iom_state_t *s = handle;
    uint32_t status = 0u;

    if (!iom_handle_ok(s))
        return 2u;
    uint32_t module = s->module;

    if (s->hp) {
        s->txn_int |= mask;
        if (s->txn_int & IOM_INT_CMDCMP_DERR) {
            /* Wait for DMA completion too, unless DMA was never enabled. */
            if (!(IOM_REG(module, IOM_DMACFG) & 1u) || (s->txn_int & IOM_INT_DCMP_ERR)) {
                s->last_hp_idx++;
                s->num_hp--;
                g2_iom_dma_entry_t *e = &s->hp_txn[s->last_hp_idx % s->max_hp];
                if (e->callback != NULL) {
                    e->callback(e->callback_ctxt,
                                (uint32_t)audio_ble_vendor_finish_55bd70(module, s->txn_int));
                    e->callback = NULL;
                }
                if (s->txn_int & IOM_INT_ERR) {
                    IOM_REG(module, IOM_DMACFG) &= ~1u;
                    IOM_REG(module, IOM_DMASTAT) = 0u;
                    audio_ble_vendor_recover_55bdac((uint8_t *)s, s->txn_int & IOM_INT_ERR);
                }
                if (s->num_hp != 0u) {
                    IOM_REG(module, IOM_DMASTAT) = 0u;
                    s->txn_int = 0u;
                    am_hal_iom_program_dma_55c174(s);
                } else {
                    s->hp = 0u;
                    IOM_REG(module, IOM_INTEN) &= 0xfffffbfeu; /* ~(DCMP | CMDCMP) */
                    IOM_REG(module, IOM_CQSETCLEAR) = IOM_SC_UNPAUSE_CQ;
                }
            }
        }
        return 0u;
    }

    if (s->num_pend != 0u) {
        uint32_t cq[4];
        if (s->cmdq != 0u &&
            (status = display_driver_uled_mspi_queue_snapshot_53901a(s->cmdq, cq)) == 0u) {
            s->restart = 0u;
            while (s->last_idx_processed != cq[0] && !s->restart) {
                s->last_idx_processed++;
                s->num_pend--;
                uint32_t i = s->last_idx_processed & 0xffu;
                if (s->callback[i] != NULL) {
                    s->callback[i](s->callback_ctxt[i], 0u);
                    if (s->seq != 2u)
                        s->callback[i] = NULL;
                }
            }
            if (!s->restart && (mask & IOM_INT_ERR)) {
                s->last_idx_processed++;
                s->num_pend--;
                uint32_t i = s->last_idx_processed & 0xffu;
                if (s->callback[i] != NULL) {
                    s->callback[i](s->callback_ctxt[i],
                                   (uint32_t)audio_ble_vendor_finish_55bd70(module, mask));
                    if (s->seq != 2u)
                        s->callback[i] = NULL;
                }
                IOM_REG(module, IOM_CQCFG) &= ~1u;
                IOM_REG(module, IOM_DMACFG) &= ~1u;
                IOM_REG(module, IOM_DMASTAT) = 0u;
                audio_ble_vendor_recover_55bdac((uint8_t *)s, mask & IOM_INT_ERR);
                (void)display_driver_uled_mspi_queue_release_5390fc(s->cmdq);
                if (s->num_pend != 0u)
                    audio_ble_vendor_option_before_store_55c13a(s);
            }
            if (s->num_pend == 0u)
                audio_ble_vendor_option_after_load_55c168(s);
        }
        if (s->num_pend == 0u) {
            /* IOM_SET_INTEN: restore the user interrupt configuration. */
            IOM_REG(module, IOM_INTEN) = 0u;
            IOM_REG(module, IOM_INTCLR) = 0xffffffffu;
            IOM_REG(module, IOM_INTEN) = s->user_int_cfg;
        }
    }
    return status;
}
