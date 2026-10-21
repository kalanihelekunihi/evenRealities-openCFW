/* Experimental Apollo Main provider candidate.
 * The empty-needle rule follows the native-attributed bootloader logger
 * strstr body in g2/src/apollo-bootloader/initializer-callbacks/elog_output.c.
 * Nonempty search delegates to the pinned NationalChip memmem C source.
 * This is a semantic source reduction, not a stock Main byte match.
 */
#include <stddef.h>

extern size_t strlen(const char *);
extern void *memmem(const void *, size_t, const void *, size_t);

char *strstr(const char *haystack, const char *needle)
{
    if (*needle == '\0')
        return (char *)haystack;
    return (char *)memmem(haystack, strlen(haystack), needle, strlen(needle));
}
