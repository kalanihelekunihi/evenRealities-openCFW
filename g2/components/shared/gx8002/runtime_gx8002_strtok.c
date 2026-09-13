/* SPDX-License-Identifier: MIT */
extern char *open_cfw_gx8002_strtok_saved;
char *open_cfw_gx8002_strtok(char *text, const char *delimiters)
{
    const char *scan;
    char *token;
    unsigned int c, separator;
    if (!text && !(text=open_cfw_gx8002_strtok_saved)) return 0;
    /* Skip delimiters, then terminate the next nonempty token in place. */
skip:
    c=(unsigned char)*text++;
    for (scan=delimiters; (separator=(unsigned char)*scan++);)
        if (c==separator) goto skip;
    if (!c) { open_cfw_gx8002_strtok_saved=0; return 0; }
    token=text-1;
    for (;;) {
        c=(unsigned char)*text++;
        scan=delimiters;
        do {
            separator=(unsigned char)*scan++;
            if (c==separator) {
                if (!c) text=0;
                else text[-1]=0;
                open_cfw_gx8002_strtok_saved=text;
                return token;
            }
        } while (separator);
    }
}
