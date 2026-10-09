# Codec UART3 readable drain

```c
empty(q) { return q.write==q.read; }
get(q,out) {
    if(empty(q))return 0;
    *out=q.storage[q.read]; q.read=(q.read+1)&q.mask;return 1;
}
read(q,out,max) {
    if(empty(q))return 0;
    n=0; while(n<max && get(q,out)){n++;out++;}return n;
}
codec_uart_read(out,max) { return read((ring*)0x20073ED4,out,max); }
```

storage200731B0,mask63. Mask requires valid power-of-two geometry. Last63 bytes survive a205byte initial staging burst under tested overwrite-oldest rule, then reads drain in retained order. This is synthetic pressure/copy, not an observed device burst. Temple-sync stream global20074B14 and loggerstream200748BC are separate consumers; no shared route inferred.
