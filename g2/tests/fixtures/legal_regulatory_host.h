#include <stdint.h>

extern uintptr_t open_cfw_test_legal_root;
extern uintptr_t open_cfw_test_legal_animation_object;
void open_cfw_test_legal_page_create(uintptr_t context);
void open_cfw_test_legal_scroll(uintptr_t object, int32_t delta, uint32_t animated);
void open_cfw_test_legal_animate(uintptr_t object, uint32_t duration, uint32_t delay);

#define OPEN_CFW_LEGAL_REGULATORY_PAGE_CREATE(c) open_cfw_test_legal_page_create(c)
#define OPEN_CFW_LEGAL_REGULATORY_SCROLL(o,d,a) open_cfw_test_legal_scroll((o),(d),(a))
#define OPEN_CFW_LEGAL_REGULATORY_ANIMATE(o,d,l) open_cfw_test_legal_animate((o),(d),(l))
#define OPEN_CFW_LEGAL_REGULATORY_ROOT() open_cfw_test_legal_root
#define OPEN_CFW_LEGAL_REGULATORY_ANIMATION_OBJECT open_cfw_test_legal_animation_object
