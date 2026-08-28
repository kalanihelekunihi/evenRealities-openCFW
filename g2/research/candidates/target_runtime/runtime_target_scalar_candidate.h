/*
 * SPDX-License-Identifier: MIT
 *
 * Isolated scalar runtime provider candidate for Cortex-M55 admission tests.
 */

#ifndef OPEN_CFW_RUNTIME_TARGET_SCALAR_CANDIDATE_H
#define OPEN_CFW_RUNTIME_TARGET_SCALAR_CANDIDATE_H

typedef __SIZE_TYPE__ open_cfw_target_size;

void *open_cfw_target_memchr(const void *buffer, int value,
                             open_cfw_target_size count);
int open_cfw_target_memcmp(const void *first, const void *second,
                          open_cfw_target_size count);
void *open_cfw_target_memcpy(void *destination, const void *source,
                            open_cfw_target_size count);
void *open_cfw_target_memmove(void *destination, const void *source,
                             open_cfw_target_size count);
void *open_cfw_target_memset(void *destination, int value,
                            open_cfw_target_size count);

char *open_cfw_target_strcat(char *destination, const char *source);
int open_cfw_target_strcmp(const char *first, const char *second);
char *open_cfw_target_strcpy(char *destination, const char *source);
open_cfw_target_size open_cfw_target_strlen(const char *text);
int open_cfw_target_strncmp(const char *first, const char *second,
                           open_cfw_target_size count);
char *open_cfw_target_strncpy(char *destination, const char *source,
                              open_cfw_target_size count);
char *open_cfw_target_strrchr(const char *text, int value);
char *open_cfw_target_strstr(const char *text, const char *needle);

void open_cfw_target_qsort(
    void *base,
    open_cfw_target_size count,
    open_cfw_target_size width,
    int (*compare)(const void *, const void *)
);

float open_cfw_target_fabsf(float value);
float open_cfw_target_floorf(float value);
float open_cfw_target_fmaxf(float first, float second);
float open_cfw_target_fminf(float first, float second);
float open_cfw_target_roundf(float value);
float open_cfw_target_sqrtf(float value);
float open_cfw_target_truncf(float value);

#endif
