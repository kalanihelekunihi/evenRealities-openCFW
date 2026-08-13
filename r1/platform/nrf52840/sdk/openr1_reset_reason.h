#ifndef OPENR1_RESET_REASON_H
#define OPENR1_RESET_REASON_H

#include <stdbool.h>

#include "openr1/r1_reset_reason.h"

void openr1_reset_reason_initialize(void);
bool openr1_reset_reason_latest(r1_reset_reason_report *report);

#endif
