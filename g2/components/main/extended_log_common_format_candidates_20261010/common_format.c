#include <stdint.h>

typedef struct {
    uint8_t *destination;
    uint32_t capacity;
    uint32_t count;
} writer;

static void put(writer *w, uint8_t c)
{
    if (w->capacity && w->count < w->capacity-1u) w->destination[w->count]=c;
    w->count++;
}

static void padded(writer *w, const uint8_t *data, uint32_t length,
                   uint32_t width, uint32_t left, uint32_t zero,
                   uint32_t prefix)
{
    uint32_t spaces=width>length?width-length:0u;
    if (!left && zero && prefix) {
        for (uint32_t i=0;i<prefix;i++) put(w,data[i]);
        data+=prefix; length-=prefix;
    }
    if (!left) while (spaces--) put(w,zero?'0':' ');
    while (length--) put(w,*data++);
    if (left) while (spaces--) put(w,' ');
}

static uint32_t digits(uint8_t *out, uint32_t value, uint32_t base,
                       uint32_t upper)
{
    uint8_t reversed[32]; uint32_t n=0,k=0;
    do {
        uint32_t d=value%base;
        reversed[n++]=(uint8_t)(d<10u?'0'+d:(upper?'A':'a')+d-10u);
        value/=base;
    } while (value);
    while (n) out[k++]=reversed[--n];
    return k;
}

/* Decimal conversion by long multiplication; uses only 32-bit operations. */
static uint32_t digits64(uint8_t *out, uint32_t low, uint32_t high)
{
    volatile uint8_t decimal[20];
    for (uint32_t i=0;i<20u;i++) decimal[i]=0u;
    for (uint32_t bit=64u;bit;bit--) {
        uint32_t b=bit-1u;
        uint32_t carry=b>=32u ? ((high>>(b-32u))&1u) : ((low>>b)&1u);
        for (uint32_t i=20u;i;i--) {
            uint32_t n=(uint32_t)decimal[i-1u]*2u+carry;
            decimal[i-1u]=(uint8_t)(n%10u);
            carry=n/10u;
        }
    }
    uint32_t start=0u;
    while (start<19u && decimal[start]==0u) start++;
    uint32_t count=0u;
    while (start<20u) out[count++]=(uint8_t)('0'+decimal[start++]);
    return count;
}

/* Bounded 0x44b76c candidate for validated integer/string forms. Supported
 * flags: '-', '#', '0'; decimal field width <= 24; string precision numeric
 * or '*'; optional single 'l' or 'z' on 32-bit integer; 'll' decimal on
 * two little-endian argument words. No floating point. */
int32_t g2_log_candidate_common_format(uint32_t destination_word,
                                        uint32_t capacity,
                                        uint32_t format_word,
                                        uint32_t arguments_word)
{
    writer w={(uint8_t *)(uintptr_t)destination_word,capacity,0};
    const uint8_t *fmt=(const uint8_t *)(uintptr_t)format_word;
    const uint32_t *args=(const uint32_t *)(uintptr_t)arguments_word;
    while (*fmt) {
        uint8_t c=*fmt++;
        if (c!='%') { put(&w,c); continue; }
        c=*fmt++;
        if (c=='%') { put(&w,'%'); continue; }
        if (c==0u) { put(&w,'%'); break; }
        uint32_t left=0,alternate=0,zero=0,width=0,precision=0xffffffffu;
        for (;;) {
            if (c=='-') left=1;
            else if (c=='#') alternate=1;
            else if (c=='0') zero=1;
            else break;
            c=*fmt++;
        }
        while (c>='0'&&c<='9') { width=width*10u+c-'0'; c=*fmt++; }
        if (c=='.') {
            c=*fmt++; precision=0;
            if (c=='*') { precision=*args++; c=*fmt++; }
            else while (c>='0'&&c<='9') {
                precision=precision*10u+c-'0'; c=*fmt++;
            }
        }
        uint32_t length=0;
        if (c=='l') {
            length=1u;c=*fmt++;
            if (c=='l') { length=2u;c=*fmt++; }
        } else if (c=='z') { length=1u;c=*fmt++; }
        uint32_t value=*args++;
        if (length==2u && (c=='u'||c=='d')) {
            uint32_t high=*args++;
            uint8_t data[22];uint32_t n=0;
            if (c=='d' && (high&0x80000000u)) {
                data[n++]='-';
                value=~value+1u;
                high=~high+(value==0u);
            }
            n+=digits64(data+n,value,high);
            padded(&w,data,n,width,left,zero,n&&data[0]=='-'?1u:0u);
        } else if (c=='d'||c=='u'||c=='x'||c=='X'||c=='p') {
            uint8_t data[35];uint32_t n=0,prefix=0;
            if (c=='d' && (value&0x80000000u)) {
                data[n++]='-'; value=0u-value;prefix=1;
            }
            if ((c=='x'||c=='X')&&alternate&&value) {
                data[n++]='0';data[n++]=c;prefix=2;
            }
            n+=digits(data+n,value,(c=='d'||c=='u')?10u:16u,c=='X');
            padded(&w,data,n,width,left,zero,prefix);
        } else if (c=='c') {
            uint8_t character=(uint8_t)value;
            padded(&w,&character,1u,width,left,0u,0u);
        } else if (c=='s') {
            const uint8_t *str=(const uint8_t *)(uintptr_t)value;
            if (!str) str=(const uint8_t *)"(null)";
            uint32_t bytes=0;
            while (str[bytes] && bytes<precision) bytes++;
            padded(&w,str,bytes,width,left,0u,0u);
        } else __builtin_unreachable();
    }
    if (capacity) w.destination[w.count<capacity?w.count:capacity-1u]=0;
    return (int32_t)w.count;
}
