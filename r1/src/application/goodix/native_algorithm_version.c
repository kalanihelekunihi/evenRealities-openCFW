#include <stdint.h>
#include <stddef.h>

/* Native Goodix version ABI. These entry points take the caller's buffer;
 * the older capacity-taking goodix_primitives models are a separate API. */
static size_t version_length(const char *s)
{
    size_t n=0; while (s[n]) ++n; return n;
}
static void version_copy(char *out,const char *in,size_t count)
{
    for (size_t i=0;i<count;++i) out[i]=in[i];
}
static char *version_append(char *out,const char *in)
{
    size_t n=version_length(out),i=0;
    do { out[n+i]=in[i]; } while (in[i++]);
    return out;
}
static char *version_bounded_copy(char *out,const char *in,size_t count)
{
    size_t i=0;
    while (i<count && in[i]) { out[i]=in[i]; ++i; }
    while (i<count) out[i++]=0;
    return out;
}
const char *GH3x2xAdtVersion(void)
{
    return "GX_HARDADT_SOFTCHECK_v0.1";
}
char *r1_goodix_dlcom_version(char *out)
{
    version_bounded_copy(out,"dlCom_pre2exc",14);
    version_append(out,"_pv"); version_append(out,"_v1.3.0");
    version_append(out,"_"); return version_append(out,"c00c91c9");
}
char *r1_goodix_dsp_version(char *out)
{
    version_copy(out,"dsp",4);
    version_append(out,"_pv"); version_append(out,"_v1.3.0");
    version_append(out,"_"); return version_append(out,"30234f22");
}
uint32_t r1_goodix_version_qualifier(char *out)
{
    /* The native helper writes two bytes and deliberately omits a terminator. */
    if (out) { out[0]='n'; out[1]='c'; }
    return 1;
}
/* The stock weights helper copies50 bytes past this string into adjacent
 * instructions. Only its terminated text escapes the private caller buffer.
 * This private helper supplies that text without embedding executable bytes;
 * it is not an implementation of the unchecked native helper's public ABI. */
static void weights_version_text(char out[52])
{
    (void)version_bounded_copy(out,"gh3x2x-v2.23_7ecd2a",50);
}
int32_t goodix_hba_version(char *out)
{
    char qualifier[8]={0},buffer[100]={0};
    version_copy(out,"GH_HR_exc",10);
    version_append(out,"_pv"); version_append(out,"_v2.0.3.0");
    version_append(out,"_"); version_append(out,"CONF");
    (void)r1_goodix_version_qualifier(qualifier);
    if (version_length(qualifier)) { version_append(out,"_"); version_append(out,qualifier); }
    version_append(out,"_"); version_append(out,"21d2063d");
    version_append(out,"_"); version_append(out,"002271a1"); version_append(out,"\n");
    r1_goodix_dsp_version(buffer); version_append(out,buffer); version_append(out,"\n");
    r1_goodix_dlcom_version(buffer); version_append(out,buffer); return 0;
}
int32_t goodix_hrv_version(char *out)
{
    version_copy(out,"GH_HRV_pre",11);
    version_append(out,"_pv"); version_append(out,"_v1.0.1.0");
    version_append(out,"_"); version_append(out,"ed953ff3"); return 0;
}
int32_t goodix_nadt_version(char *out)
{
    char qualifier[8]={0},buffer[100]={0};
    version_copy(out,"GH_NADT_pre",12);
    version_append(out,"_pv"); version_append(out,"_v1.0.2.0");
    (void)r1_goodix_version_qualifier(qualifier);
    if (version_length(qualifier)) { version_append(out,"_"); version_append(out,qualifier); }
    version_append(out,"_"); version_append(out,"548d894d"); version_append(out,"\n");
    r1_goodix_dsp_version(buffer); version_append(out,buffer); return 0;
}
int32_t goodix_spo2_version(char *out)
{
    char weights[52],qualifier[8]={0},buffer[52]={0};
    version_bounded_copy(out,"GH_SPO2_pre_pv_v2.1.10.0",25);
    weights_version_text(weights);
    version_append(out,"("); version_append(out,weights); version_append(out,")");
    (void)r1_goodix_version_qualifier(qualifier);
    if (version_length(qualifier)) { version_append(out,"_"); version_append(out,qualifier); }
    version_append(out,"_"); version_append(out,"277e89de"); version_append(out,"\n");
    version_append(out,"net_"); version_append(out,"1f1cf98b"); version_append(out,"\n");
    r1_goodix_dsp_version(buffer); version_append(out,buffer); version_append(out,"\n");
    r1_goodix_dlcom_version(buffer); version_append(out,buffer); return 0;
}
void GH3X2X_AlgoVersion(uint8_t function_id,char *out)
{
    if (!out) return;
    switch (function_id) {
    case 0: {
        const char *first=GH3x2xAdtVersion();
        size_t count=version_length(first)+1;
        version_copy(out,GH3x2xAdtVersion(),count); break;
    }
    case 1: (void)goodix_hba_version(out); break;
    case 2: (void)goodix_hrv_version(out); break;
    case 6: (void)goodix_spo2_version(out); break;
    case 9: case 15: (void)goodix_nadt_version(out); break;
    default: version_copy(out,"no_ver",7); break;
    }
}
