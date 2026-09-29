
int gx8002_uart_write(int param_1,undefined4 *param_2,int param_3)

{
  undefined4 *puVar1;
  int iVar2;
  
  iVar2 = param_1 * 0x80 + DAT_1020362c;
  for (puVar1 = param_2; (int)puVar1 - (int)param_2 < param_3;
      puVar1 = (undefined4 *)((int)puVar1 + 1)) {
    dw_uart_putc(iVar2,*puVar1);
  }
  return (uint)(-1 < param_3) * param_3;
}

