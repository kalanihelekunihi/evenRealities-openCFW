/* Native image-B 0x100112d4..0x1001133f, strtok-style tokenizer.
 * The saved cursor is the actual mutable SRAM word at 0x2002d3e0.
 * Its initial value and final linker placement remain product contracts.
 * Native SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>
#include <stddef.h>

extern char *gx8002_image_b_token_cursor_2002d3e0;
static char **const saved_cursor =
    &gx8002_image_b_token_cursor_2002d3e0;

static int is_separator(char value, const char *separators)
{
    for (const char *p = separators; *p != '\0'; ++p) {
        if (*p == value) return 1;
    }
    return 0;
}

char *gx8002_image_b_tokenize_100112d4(
    char *input, const char *separators)
{
    if (input == NULL) {
        input = *saved_cursor;
        if (input == NULL) return NULL;
    }
    while (*input != '\0' && is_separator(*input, separators)) ++input;
    if (*input == '\0') {
        *saved_cursor = NULL;
        return NULL;
    }
    char *token = input;
    while (*input != '\0') {
        if (is_separator(*input, separators)) {
            *input = '\0';
            *saved_cursor = input + 1;
            return token;
        }
        ++input;
    }
    *saved_cursor = NULL;
    return token;
}
