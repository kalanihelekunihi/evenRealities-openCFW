/* BSS pointer cells written by native thread-pool startup 0x49137a.
 * Native RAM cells: queue 0x20074aa0, mutex 0x20074aa4. */
/* audio_uart_pool_queue: stock 0x20074aa0 is one cell; defined as an alias of audio_uart_timeout_queue (Fix 31). */
extern void * audio_uart_pool_queue;
/* audio_uart_pool_mutex: stock 0x20074aa4 is one cell; defined as an alias of audio_uart_timeout_mutex (Fix 31). */
extern void * audio_uart_pool_mutex;
