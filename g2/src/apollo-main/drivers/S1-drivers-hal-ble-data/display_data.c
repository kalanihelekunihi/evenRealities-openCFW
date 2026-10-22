/* Display-driver storage (S1 storage-definition pass, 2.2.6.10).
 *
 * Stock owners: platform\display_mgr\displaydrv_manager.c (manager record),
 * driver\uled\drv_mspi_uled*.c (uLED driver/panel cells), and the two
 * app\gui test/legal pages whose UI-registry contexts are referenced from
 * drivers/display. Initialised values come from the decoded 0x20000000 init
 * stream (scatter record 0x75d3f4); every other cell lies in the zero-init
 * range 0x20004558..0x20075048. Placement at the stock addresses is a linker
 * gate; this file only owns the objects. */
#include <stdint.h>

/* ---- displaydrv_manager.c ---------------------------------------------- */

/* Thread-manager record (slot 12, viewed by thread_manager.c as
 * {init, deinit, thread, queue}); the manager thread fills +0x8/+0xc. */
struct display_driver_manager {
    void (*thread_init)(void); /* +0x0 Disp_ThreadInit 0x473952 */
    void (*deinit)(void);      /* +0x4 0x473aa4 thread terminate */
    void *thread;              /* +0x8 osThreadId_t */
    void *queue;               /* +0xc osMessageQueueId_t */
};
_Static_assert(sizeof(struct display_driver_manager) == 16u, "display driver manager ABI");

extern void audio_display_driver_thread_init(void);       /* 0x473952 Disp_ThreadInit */
extern void display_driver_thread_terminate_473aa4(void); /* 0x473aa4 */

/* RAM 0x20000658 (.data): init stream words 0x00473953 0x00473aa5 0 0.
 * +4 is the terminate entry 0x473aa4, not DISP_MessageQueueInit (0x4739fc,
 * which Disp_ThreadInit's caller runs separately). */
struct display_driver_manager audio_display_driver_manager = {
    audio_display_driver_thread_init,
    display_driver_thread_terminate_473aa4,
    0,
    0,
};

/* ---- drv_mspi_uled.c / drv_mspi_uled_common.c -------------------------- */

void *volatile display_driver_uled_instance;   /* RAM 0x20074530, g2_uled_driver_t * */
void *g2_a6ng_mspi_handle;                      /* RAM 0x20074510 */
uint8_t *g2_a6ng_framebuffer;                   /* RAM 0x20074514, 640x480 4-bpp */
void *g2_jbd4010_mspi_handle;                   /* RAM 0x20074524 */
uint8_t *g2_jbd4010_framebuffer;                /* RAM 0x20074528 */
void *g2_uled_mspi_semaphore;                   /* RAM 0x20074534, binary semaphore */
const void *g2_uled_mspi_serial_config;         /* RAM 0x20074538 */
const void *g2_uled_mspi_quad_config;           /* RAM 0x2007453c */

/* RAM 0x20074130: DMA-able copy of the A6N-G column-window frame (8 bytes,
 * refilled from ROM 0x78d484 before every status write). */
__attribute__((aligned(4))) uint8_t g2_a6ng_status_frame[8];

/* ---- UI-registry page contexts (28-byte records) ------------------------ */

/* Shape shared by the registry contexts at 0x20000b1c/0x20000b38/
 * 0x20002ca8/...: +0 page id, +4 root object (set by the page on start),
 * +0x14..+0x17 flags, +0x18 input handler. */
typedef struct {
    uint32_t page_id;       /* +0x00 */
    uint32_t root;          /* +0x04 lv_obj_t * */
    uint32_t reserved[3];   /* +0x08 */
    uint8_t flags[4];       /* +0x14 */
    uint32_t (*input)(uint32_t, uint32_t, uint32_t, const uint8_t *); /* +0x18 */
} g2_ui_registry_context_t;
_Static_assert(sizeof(g2_ui_registry_context_t) == 28u, "registry context stride");

extern uint32_t legal_regulatory_input_handler_5bf146(uint32_t, uint32_t, uint32_t,
                                                      const uint8_t *); /* 0x5bf146 */
extern uint32_t semantic_distortion_predicate_true_5cf32c(uint32_t, uint32_t, uint32_t,
                                                          const uint8_t *); /* 0x5cf32c */

/* RAM 0x200014cc (.data), legal_regulatory.c page 0x109:
 * 09 01 00 00 | 0 x4 | 00 00 00 01 | 0x005bf147. */
g2_ui_registry_context_t audio_uart_registry_context_200014cc = {
    0x109u, 0u, {0u, 0u, 0u}, {0x00u, 0x00u, 0x00u, 0x01u},
    legal_regulatory_input_handler_5bf146,
};

/* RAM 0x20003064 (.data), PdtDistortionTest page 0x110:
 * 10 01 00 00 | 0 x4 | 00 00 64 01 | 0x005cf32d. */
g2_ui_registry_context_t audio_uart_registry_context_20003064 = {
    0x110u, 0u, {0u, 0u, 0u}, {0x00u, 0x00u, 0x64u, 0x01u},
    semantic_distortion_predicate_true_5cf32c,
};
