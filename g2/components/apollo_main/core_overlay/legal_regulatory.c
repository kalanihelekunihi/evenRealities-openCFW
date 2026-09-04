/* SPDX-License-Identifier: MIT */
/* Clean-room G2 legal/regulatory event policy. */

#include <stdint.h>

struct open_cfw_legal_regulatory_event {
    uint32_t action;
    int32_t scroll_delta;
};

#ifndef OPEN_CFW_LEGAL_REGULATORY_PAGE_CREATE
void open_cfw_retained_legal_regulatory_page_create(uintptr_t context);
#define OPEN_CFW_LEGAL_REGULATORY_PAGE_CREATE(context) \
    open_cfw_retained_legal_regulatory_page_create((context))
#endif

#ifndef OPEN_CFW_LEGAL_REGULATORY_SCROLL
void open_cfw_retained_legal_regulatory_scroll(
    uintptr_t object, int32_t delta, uint32_t animated);
#define OPEN_CFW_LEGAL_REGULATORY_SCROLL(object, delta, animated) \
    open_cfw_retained_legal_regulatory_scroll((object), (delta), (animated))
#endif

#ifndef OPEN_CFW_LEGAL_REGULATORY_ANIMATE
void open_cfw_retained_legal_regulatory_animate(
    uintptr_t object, uint32_t duration, uint32_t delay);
#define OPEN_CFW_LEGAL_REGULATORY_ANIMATE(object, duration, delay) \
    open_cfw_retained_legal_regulatory_animate((object), (duration), (delay))
#endif

#ifndef OPEN_CFW_LEGAL_REGULATORY_ROOT
#define OPEN_CFW_LEGAL_REGULATORY_ROOT() \
    (*(volatile uintptr_t *)(uintptr_t)0x200746A4u)
#endif

#ifndef OPEN_CFW_LEGAL_REGULATORY_ANIMATION_OBJECT
#define OPEN_CFW_LEGAL_REGULATORY_ANIMATION_OBJECT \
    (*(volatile uintptr_t *)(uintptr_t)0x200014D0u)
#endif

int open_cfw_legal_regulatory_ui_event_handler(
    uint32_t event_id,
    const struct open_cfw_legal_regulatory_event *event,
    uint32_t event_size,
    uintptr_t context)
{
    uintptr_t root;

    (void)event_size;
    if (event_id == 2u) {
        OPEN_CFW_LEGAL_REGULATORY_PAGE_CREATE(context);
        root = OPEN_CFW_LEGAL_REGULATORY_ROOT();
        OPEN_CFW_LEGAL_REGULATORY_ANIMATION_OBJECT = root;
        OPEN_CFW_LEGAL_REGULATORY_ANIMATE(root, 250u, 0u);
    } else if (event_id == 3u && event != (const void *)0
               && event->action == 1u) {
        root = OPEN_CFW_LEGAL_REGULATORY_ROOT();
        OPEN_CFW_LEGAL_REGULATORY_SCROLL(root, event->scroll_delta, 1u);
    }
    return 0;
}
