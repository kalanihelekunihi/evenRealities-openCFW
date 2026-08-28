/* SPDX-License-Identifier: MIT */

__attribute__((used, noinline))
char *open_cfw_bootloader_strstr(
    const char *haystack,
    const char *needle
)
{
    const char *candidate;
    const char *left;
    const char *right;

    if (*needle == '\0') {
        return (char *)haystack;
    }
    for (candidate = haystack; *candidate != '\0'; ++candidate) {
        left = candidate;
        right = needle;
        while (*left == *right) {
            ++right;
            if (*right == '\0') {
                return (char *)candidate;
            }
            ++left;
        }
    }
    return (char *)0;
}
