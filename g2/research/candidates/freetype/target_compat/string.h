/* SPDX-License-Identifier: FTL */
/* Declaration-only bare-target boundary; see ../README.md. */
#ifndef OPEN_CFW_FREETYPE_TARGET_STRING_H
#define OPEN_CFW_FREETYPE_TARGET_STRING_H
#include <stddef.h>
void *memchr(const void *buffer, int value, size_t count);
int memcmp(const void *first, const void *second, size_t count);
void *memcpy(void *destination, const void *source, size_t count);
void *memmove(void *destination, const void *source, size_t count);
void *memset(void *destination, int value, size_t count);
char *strcat(char *destination, const char *source);
int strcmp(const char *first, const char *second);
char *strcpy(char *destination, const char *source);
size_t strlen(const char *text);
int strncmp(const char *first, const char *second, size_t count);
char *strncpy(char *destination, const char *source, size_t count);
char *strrchr(const char *text, int value);
char *strstr(const char *text, const char *needle);
#endif
