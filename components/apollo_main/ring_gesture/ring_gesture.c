/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Even Realities G2 ring long-press forwarding for the blob-backed openCFW
 * Apollo main application.
 *
 * Derived from jimrandomh/g2flash patches/gesture_fwd.c at commit
 * 6d5c58598e047ca5980065a9ee7570ce2d172ca7. The firmware addresses below are
 * specific to the reviewed G2 2.2.6.10 application.
 */

typedef int (*post_ui_event_fn)(void *context, int code, void *data);
typedef int *(*foreground_mode_fn)(void *global_context);
typedef int (*send_system_event_fn)(int, int, int, int, int, int);

#define STOCK_POST_UI_EVENT \
    ((post_ui_event_fn)0x0045F8FDU)
#define STOCK_FOREGROUND_MODE \
    ((foreground_mode_fn)0x0045F8E7U)
#define STOCK_SEND_SYSTEM_EVENT \
    ((send_system_event_fn)0x004DA16BU)

#define FOREGROUND_UI_CONTEXT (*(void *volatile *)0x200744D0U)
#define CURRENT_INPUT_SOURCE (*(volatile unsigned char *)0x2034DC30U)

#define EVENHUB_APPLICATION_ID 0xE0
#define RING_LONG_PRESS_EVENT 9
#define RING_LONG_PRESS_RELEASE_EVENT 10
#define RING_INPUT_SOURCE 4

/*
 * The patched call site is already inside the EvenHub long-press branch.
 * Forward only ring-originated events; the touchpad shares the surrounding
 * input subtype and must not produce a ring event.
 */
__attribute__((used, noinline))
void evenhub_longpress(void)
{
    if (CURRENT_INPUT_SOURCE == RING_INPUT_SOURCE) {
        STOCK_SEND_SYSTEM_EVENT(0, 0, 0, RING_LONG_PRESS_EVENT, 0, 0);
    }
}

/*
 * The stock release path posts UI event 0x4a, which EvenHub drops. When the
 * source is the ring and EvenHub is foreground, send the paired system event
 * directly. All other inputs retain the original UI-event call.
 */
__attribute__((used, noinline))
int ring_release(void *context, int code, void *data)
{
    if (CURRENT_INPUT_SOURCE == RING_INPUT_SOURCE) {
        int *foreground = STOCK_FOREGROUND_MODE(FOREGROUND_UI_CONTEXT);
        if (foreground != (void *)0
                && *foreground == EVENHUB_APPLICATION_ID) {
            STOCK_SEND_SYSTEM_EVENT(
                0,
                0,
                0,
                RING_LONG_PRESS_RELEASE_EVENT,
                0,
                0
            );
            return 1;
        }
    }
    return STOCK_POST_UI_EVENT(context, code, data);
}

