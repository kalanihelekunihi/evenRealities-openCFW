/* Fixed CASE image's weak HAL_UART_ErrorCallback is exactly a no-op. */
void HAL_UART_ErrorCallback(void *handle) { (void)handle; }
