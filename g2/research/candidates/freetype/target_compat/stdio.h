/* SPDX-License-Identifier: FTL */
/* Declaration-only bare-target boundary; see ../README.md. */
#ifndef OPEN_CFW_FREETYPE_TARGET_STDIO_H
#define OPEN_CFW_FREETYPE_TARGET_STDIO_H
#include <stddef.h>
typedef struct open_cfw_freetype_target_file FILE;
int fclose(FILE *stream);
FILE *fopen(const char *path, const char *mode);
size_t fread(void *buffer, size_t size, size_t count, FILE *stream);
int fseek(FILE *stream, long offset, int origin);
long ftell(FILE *stream);
int sprintf(char *buffer, const char *format, ...);
#ifndef SEEK_SET
#define SEEK_SET 0
#endif
#endif
