/* Onboarding news page, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_news_page.c.
 * Native 0x50a010..0x50a07d (literal 150.0f at 0x50a090). Kept apart from
 * ui_onboarding_news_page.c because it is the only FPU code of the first half
 * of the TU: profile g2-apollo-main-3 (single precision, integer interface). */
#include <stdint.h>

int32_t onboarding_news_scroll_calc_anim_time_50a010(int32_t speed, int32_t distance);

/* Scroll animation time in ms from gesture speed and distance (both clamped
 * to 1..200): faster gestures and longer distances give shorter animations,
 * clamped to 80..400 ms. The only caller (0x50b744) discards the result and
 * animates for a fixed 250 ms. */
int32_t onboarding_news_scroll_calc_anim_time_50a010(int32_t speed, int32_t distance)
{
    if (speed < 1)
        speed = 1;
    else if (speed > 200)
        speed = 200;
    if (distance < 1)
        distance = 1;
    else if (distance > 200)
        distance = 200;
    int32_t base = 400 - (speed * 320) / 200;
    float scale = 150.0f / (float)(distance + 10);
    int32_t time_ms = (int32_t)((float)base * scale);
    if (time_ms < 80)
        time_ms = 80;
    else if (time_ms > 400)
        time_ms = 400;
    return time_ms;
}
