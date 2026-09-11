/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_STAGE2_LIBC_H
#define OPEN_CFW_GX8002_STAGE2_LIBC_H

#include <stddef.h>

int open_cfw_gx8002_stage2_strcmp(const char *a, const char *b);
char *open_cfw_gx8002_stage2_strchr(const char *s, int c);
size_t open_cfw_gx8002_stage2_strlen(const char *s);
size_t open_cfw_gx8002_stage2_strnlen(const char *s, size_t maxlen);

#endif
