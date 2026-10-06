/* SPDX-License-Identifier: MIT - standard C declarations for bare-metal ARM */
#ifndef OPENCFW_FREESTANDING_STRING_H
#define OPENCFW_FREESTANDING_STRING_H
#include <stddef.h>
void *memcpy(void *,const void *,size_t);
void *memset(void *,int,size_t);
int memcmp(const void *,const void *,size_t);
char *strcpy(char *,const char *);
char *strchr(const char *,int);
size_t strlen(const char *);
size_t strspn(const char *,const char *);
size_t strcspn(const char *,const char *);
#endif
