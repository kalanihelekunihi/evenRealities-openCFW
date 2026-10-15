/* Native thread-pool submit_work 0x491184 ROM diagnostics. */
const char audio_uart_work_module[]="thread_pool";
const char audio_uart_work_source[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\thread_pool.c";
const char audio_uart_work_function[]="submit_work";
const char audio_uart_work_e_unready[]="submit_work: thread pool not initialized";
const char audio_uart_work_c_unready[]="[thread_pool]submit_work: thread pool not initialized";
const char audio_uart_work_e_null[]="submit_work: invalid work function";
const char audio_uart_work_c_null[]="[thread_pool]submit_work: invalid work function";
const char audio_uart_work_e_submit[]="submit_work: submitting task for AppID %d";
const char audio_uart_work_c_submit[]="[thread_pool]submit_work: submitting task for AppID %d";
const char audio_uart_work_e_queue[]="submit_work: failed to put task to queue, error id %d";
const char audio_uart_work_c_queue[]="[thread_pool]submit_work: failed to put task to queue, error id %d";
const char audio_uart_work_e_lock[]="submit_work: failed to acquire mutex .timeout!!!";
const char audio_uart_work_c_lock[]="[thread_pool]submit_work: failed to acquire mutex .timeout!!!";
