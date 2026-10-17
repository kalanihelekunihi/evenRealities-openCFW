/* Apollo locale registry at flash 0x7560e4 and plural callbacks 0x45fec0-0x45fffa.
 * Translation-data pointer tables are initialized from authenticated Main startup RAM. */
#include <stdint.h>
#include <stddef.h>

typedef uint32_t (*plural_rule_fn)(int32_t);
typedef struct {
    const char *locale;
    void *translation_data;
    uint32_t reserved[6];
    plural_rule_fn plural_rule;
} display_locale_record;
_Static_assert(sizeof(display_locale_record)==36u,"Apollo locale record size");
_Static_assert(offsetof(display_locale_record,plural_rule)==32u,"Apollo plural callback offset");

extern const char *audio_uart_locale_data_en[157]; /* RAM 0x20001588 */
extern const char *audio_uart_locale_data_de[157]; /* RAM 0x200017fc */
extern const char *audio_uart_locale_data_es[157]; /* RAM 0x20001a70 */
extern const char *audio_uart_locale_data_fr[157]; /* RAM 0x20001ce4 */
extern const char *audio_uart_locale_data_it[157]; /* RAM 0x20001f58 */
extern const char *audio_uart_locale_data_ja[157]; /* RAM 0x200021cc */
extern const char *audio_uart_locale_data_zh_cn[157]; /* RAM 0x20002440 */
extern const char *audio_uart_locale_data_zh_hk[157]; /* RAM 0x200026b4 */

static uint32_t magnitude(int32_t value)
{
    return value<0 ? 0u-(uint32_t)value : (uint32_t)value;
}
static uint32_t singular_one(int32_t value)
{
    return magnitude(value)==1u ? 1u : 5u;
}
static uint32_t spanish_plural(int32_t value)
{
    uint32_t n=magnitude(value);
    if(n==1u) return 1u;
    return n!=0u && n%1000000u==0u ? 4u : 5u;
}
static uint32_t french_plural(int32_t value)
{
    uint32_t n=magnitude(value);
    if(n<=1u) return 1u;
    return n%1000000u==0u ? 4u : 5u;
}
static uint32_t italian_plural(int32_t value)
{
    uint32_t n=magnitude(value);
    if(n==1u) return 1u;
    return n!=0u && n%1000000u==0u ? 4u : 5u;
}
static uint32_t invariant_plural(int32_t value)
{
    (void)value;
    return 5u;
}

static const display_locale_record locales[8]={
    {"en-GB",audio_uart_locale_data_en,{0},singular_one},
    {"de",audio_uart_locale_data_de,{0},singular_one},
    {"es",audio_uart_locale_data_es,{0},spanish_plural},
    {"fr",audio_uart_locale_data_fr,{0},french_plural},
    {"it",audio_uart_locale_data_it,{0},italian_plural},
    {"ja",audio_uart_locale_data_ja,{0},invariant_plural},
    {"zh-CN",audio_uart_locale_data_zh_cn,{0},invariant_plural},
    {"zh-HK",audio_uart_locale_data_zh_hk,{0},invariant_plural},
};

const void *const audio_uart_display_context[9]={
    &locales[0],&locales[1],&locales[2],&locales[3],
    &locales[4],&locales[5],&locales[6],&locales[7],0
};
