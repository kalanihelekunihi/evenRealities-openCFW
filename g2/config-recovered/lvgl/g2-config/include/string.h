/* Not stock: the shared freestanding <string.h> plus the C library calls that
 * lv_string_clib.c makes (stock LV_USE_STDLIB_STRING == LV_STDLIB_CLIB). */
#ifndef G2_LVGL_STRING_H
#define G2_LVGL_STRING_H
#include_next <string.h>
size_t strnlen(const char *, size_t);
char *strncat(char *, const char *, size_t);
char *strchr(const char *, int);
#endif
