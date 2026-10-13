#ifndef G2_FT_ANALYSIS_STDIO_H
#define G2_FT_ANALYSIS_STDIO_H
#include <stddef.h>
typedef struct g2_ft_analysis_file FILE;
#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2
int fclose(FILE *);
FILE *fopen(const char *, const char *);
size_t fread(void *, size_t, size_t, FILE *);
int fseek(FILE *, long, int);
long ftell(FILE *);
int sprintf(char *, const char *, ...);
#endif
