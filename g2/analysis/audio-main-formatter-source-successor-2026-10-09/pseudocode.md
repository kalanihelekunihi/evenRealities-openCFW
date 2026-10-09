# Formatting and fatal-message path

```c
unsigned log(format, ...) {
    if (!registered_sink) return 0;
    args=va_start(format);
    count=format_to_buffer(shared_buffer,format,args);
    registered_sink(shared_buffer);
    return count;
}
void malloc_failed() {
    log("MallocFailed: cannot malloc memory\n");
    for (;;) {} // actual stock self-loop, not a returned allocation failure
}
```

Formatter scans literal text, optional zero padding, signed width, precision (including .*), optional l/ll and c/s/x/X/u/d/i/f/F. Unhandled specifiers emit the specifier character; %% emits%. Integer64 conversions use digit/decimal/hex helpers. %f/%F reads an aligned double and converts to float before formatting. It has no destination-capacity parameter. All selected outputs fit guarded1024-byte synthetic buffers; that is not a recovered stock buffer-capacity guarantee.

When a nonnull destination is used and translation flag is set, LF inserts CR and increases count. With null destination, the tested literal/integer/string count path leaves buffer unchanged and LF is not expanded. Do not generalize this to float dry-run sizing without testing it. Negative string width is a trailing padding-count in the recovered source: %-8s on abcdef produces abcdef followed by eight spaces (14bytes), not standard printf's total width8.
