
/* Heap callers ignore R0; preserve native variadic register ABI4733ee. */
int32_t g2_file_heap_error_log(const char *,...)
    __attribute__((alias("g2_log_transport_queue_failure")));
