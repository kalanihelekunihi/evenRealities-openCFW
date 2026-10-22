/* Page-manager accessors, stock D:\01_workspace\s200_ap510b_iar_git\framework\page_manager\page_manager.c
 * (log tag "page.mgr", see page_manager_container_event_cb 0x45f914).
 * Native 0x45f6b4..0x45f6bf, 0x45f8d0..0x45f8e5, 0x45f8fc..0x45f90f, 0x45fe04..0x45fe0f.
 *
 * The page-manager state (RAM pointer audio_uart_display_audio_handle 0x200744d0,
 * allocated by page_manager_init 0x45f15a) keeps two page slots at +0x00 and
 * +0x04 (top / base, read by 0x45f66a and 0x45f6a8), the page list at +0x08, a
 * third slot at +0x0c, and its LVGL container object at +0x18. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    void *top;        /* +0x00 foreground page (0x45f66a) */
    void *base;       /* +0x04 page under it (0x45f6a8) */
    void *list;       /* +0x08 page-entry list, linked through entry +0x20 */
    void *slot_c;     /* +0x0c read by menu_inject_event 0x461620 before a toast */
    uint8_t reserved_10[8];
    void *container;  /* +0x18 lv_obj_t receiving page events */
} g2_page_manager_t;
_Static_assert(offsetof(g2_page_manager_t, container) == 0x18, "page manager container at +0x18");

extern uint32_t audio_uart_lv_obj_event_451670(void *obj, uint32_t code, void *param); /* lv_obj_send_event */

/* Third page slot (+0x0c); NULL-safe. */
void *display_page_slot_c_get_45f6b4(g2_page_manager_t *manager)
{
    if (manager == NULL)
        return NULL;
    return manager->slot_c;
}

/* Active page: the top slot when set, otherwise the base slot. A second
 * identical body follows at 0x45f8e6 (audio_uart_display_audio_current_45f8e6). */
void *display_page_active_get_45f8d0(g2_page_manager_t *manager)
{
    if (manager == NULL)
        return NULL;
    if (manager->top != NULL)
        return manager->top;
    return manager->base;
}

/* Forward an LVGL event to the manager container; 0 when there is no manager,
 * otherwise 1 regardless of the lv_obj_send_event result. */
uint32_t display_page_send_event_45f8fc(g2_page_manager_t *manager, uint32_t code, void *param)
{
    if (manager == NULL)
        return 0u;
    (void)audio_uart_lv_obj_event_451670(manager->container, code, param);
    return 1u;
}

/* Container object of a page manager (caller 0x54eb52). */
void *display_page_root_obj_get_45fe04(g2_page_manager_t *manager)
{
    if (manager == NULL)
        return NULL;
    return manager->container;
}
