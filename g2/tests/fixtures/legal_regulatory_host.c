#include <stdint.h>

uintptr_t open_cfw_test_legal_root;
uintptr_t open_cfw_test_legal_animation_object;
uint32_t open_cfw_test_legal_page_calls;
uintptr_t open_cfw_test_legal_page_context;
uint32_t open_cfw_test_legal_scroll_calls;
uintptr_t open_cfw_test_legal_scroll_object;
int32_t open_cfw_test_legal_scroll_delta;
uint32_t open_cfw_test_legal_scroll_animated;
uint32_t open_cfw_test_legal_animate_calls;
uintptr_t open_cfw_test_legal_animate_object;
uint32_t open_cfw_test_legal_animate_duration;
uint32_t open_cfw_test_legal_animate_delay;

void open_cfw_test_legal_reset(uintptr_t root)
{
    open_cfw_test_legal_root = root;
    open_cfw_test_legal_animation_object = 0;
    open_cfw_test_legal_page_calls = 0;
    open_cfw_test_legal_page_context = 0;
    open_cfw_test_legal_scroll_calls = 0;
    open_cfw_test_legal_scroll_object = 0;
    open_cfw_test_legal_scroll_delta = 0;
    open_cfw_test_legal_scroll_animated = 0;
    open_cfw_test_legal_animate_calls = 0;
    open_cfw_test_legal_animate_object = 0;
    open_cfw_test_legal_animate_duration = 0;
    open_cfw_test_legal_animate_delay = 0;
}

void open_cfw_test_legal_page_create(uintptr_t context)
{
    ++open_cfw_test_legal_page_calls;
    open_cfw_test_legal_page_context = context;
}

void open_cfw_test_legal_scroll(uintptr_t object, int32_t delta, uint32_t animated)
{
    ++open_cfw_test_legal_scroll_calls;
    open_cfw_test_legal_scroll_object = object;
    open_cfw_test_legal_scroll_delta = delta;
    open_cfw_test_legal_scroll_animated = animated;
}

void open_cfw_test_legal_animate(uintptr_t object, uint32_t duration, uint32_t delay)
{
    ++open_cfw_test_legal_animate_calls;
    open_cfw_test_legal_animate_object = object;
    open_cfw_test_legal_animate_duration = duration;
    open_cfw_test_legal_animate_delay = delay;
}
