/* SPDX-License-Identifier: MIT */
#include <stddef.h>
int open_cfw_gx8002_strncmp(const char *left, const char *right, size_t count)
{
    while (count--) {
        unsigned char a = (unsigned char)*left;
        unsigned char b = (unsigned char)*right;
        int difference = (int)a - (int)b;
        if (difference || !a) return difference;
        ++left;
        ++right;
    }
    return 0;
}
