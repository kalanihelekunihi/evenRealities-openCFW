
void gx8002_console_initialize(undefined4 param_1)

{
  *puRam102037ec = param_1;
  gx8002_uart_initialize();
  return;
}

