/* LegalRegulatory page input handler, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\LegalRegulatory\legal_regulatory.c.
 * Native 0x5bf146..0x5bf249 (literal 0x5bf8a4 shared with the rest of the TU).
 *
 * Registered through the initialised registry context for app 0x109 (RAM
 * 0x200014cc + 0x18 holds 0x5bf147). Scroll codes are mirrored (0x44 <-> 0x45)
 * before dispatch; on the master eye a scroll posts {1, target_y} to app 0x109,
 * which the display callback 0x5bf7b8 turns into lv_obj_scroll_to_y, and 0x48
 * closes the page. Every path returns 1 (event consumed). */
#include <stdint.h>
#include <stddef.h>

#define LEGAL_APP_ID 0x109u
#define DEVICE_ROLE_MASTER 1u
#define LEGAL_SCROLL_STEP 28

enum {
    INPUT_CODE_0A = 0x0au,
    INPUT_CODE_42 = 0x42u,
    INPUT_CODE_43 = 0x43u,
    INPUT_SCROLL_UP = 0x44u,
    INPUT_SCROLL_DOWN = 0x45u,
    INPUT_CLOSE = 0x48u,
};

typedef struct {
    int32_t speed;  /* +0x00 */
    int32_t offset; /* +0x04 */
} g2_legal_scroll_input_t;

/* Payload posted to app 0x109 (decoded by 0x5bf7b8 event 3). */
typedef struct {
    uint32_t kind;     /* +0x00 1 = scroll to y */
    int32_t target_y;  /* +0x04 */
} g2_legal_scroll_msg_t;
_Static_assert(sizeof(g2_legal_scroll_msg_t) == 8, "legal scroll message");

extern uint32_t audio_legal_regulatory_root_200746a4; /* RAM 0x200746a4 page lv_obj */

extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t display_driver_uled_mode_45a568(void); /* device role, 1 = master */
extern int32_t common_ui_get_scroll_y_5546be(void *obj, int32_t delta, int32_t speed,
                                             int32_t step);
extern int32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                 uint32_t flags); /* 0x464bb2 */
extern void audio_system_alert_close_464c36(uint32_t app, uint32_t payload, uint32_t len,
                                            uint32_t flags);

uint32_t legal_regulatory_input_handler_5bf146(uint32_t arg0, uint32_t arg1, uint32_t code,
                                               const uint8_t *event)
{
    g2_legal_scroll_msg_t msg;
    const g2_legal_scroll_input_t *in;

    (void)arg0;
    (void)arg1;
    aeabi_memset_43c0e4(&msg, sizeof(msg), 0);
    aeabi_memset_43c0e4(&msg, sizeof(msg), 0);

    if (code == INPUT_SCROLL_UP)
        code = INPUT_SCROLL_DOWN;
    else if (code == INPUT_SCROLL_DOWN)
        code = INPUT_SCROLL_UP;

    switch (code) {
    case INPUT_CODE_0A:
    case INPUT_CODE_42:
    case INPUT_CODE_43:
        /* 0x42/0x43 load event+0x10 and discard it. */
        break;
    case INPUT_SCROLL_UP:
    case INPUT_SCROLL_DOWN:
        if (display_driver_uled_mode_45a568() != DEVICE_ROLE_MASTER)
            break;
        in = *(const g2_legal_scroll_input_t *const *)(event + 0x10);
        msg.kind = 1u;
        msg.target_y = common_ui_get_scroll_y_5546be(
            (void *)(uintptr_t)audio_legal_regulatory_root_200746a4,
            code == INPUT_SCROLL_UP ? -in->offset : in->offset, in->speed, LEGAL_SCROLL_STEP);
        (void)audio_uart_master_display_refresh(LEGAL_APP_ID, &msg, sizeof(msg), 0u);
        break;
    case INPUT_CLOSE:
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER)
            audio_system_alert_close_464c36(LEGAL_APP_ID, 0u, 0u, 0u);
        break;
    default:
        break;
    }
    return 1u;
}
