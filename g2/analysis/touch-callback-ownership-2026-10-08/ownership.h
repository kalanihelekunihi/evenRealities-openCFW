#ifndef OPENCFW_TOUCH_OWNERSHIP_H
#define OPENCFW_TOUCH_OWNERSHIP_H
#include <stdint.h>
/* Offline bounded helpers, not complete replacement firmware. */
void app_event(uint32_t events); /* commands 0,1,3 or >=9 only */
void touch_report_publish_slice(void); /* static 16-byte report -> TX -> attention */
#endif
