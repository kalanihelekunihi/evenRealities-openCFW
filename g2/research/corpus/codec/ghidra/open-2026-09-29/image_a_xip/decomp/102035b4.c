
void gx8002_uart_putc(int param_1,uint param_2)

{
  int iVar1;
  
  iVar1 = DAT_102035d4;
  if (param_2 == 10) {
    dw_uart_putc(DAT_102035d4 + param_1 * 0x80,0xd);
  }
  dw_uart_putc(iVar1 + param_1 * 0x80,param_2 & 0xff);
  return;
}

