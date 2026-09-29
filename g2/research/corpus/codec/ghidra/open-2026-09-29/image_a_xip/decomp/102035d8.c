
int gx8002_uart_read(int param_1,undefined1 *param_2,int param_3)

{
  undefined1 uVar1;
  undefined1 *puVar2;
  int iVar3;
  
  iVar3 = param_1 * 0x80 + DAT_10203600;
  for (puVar2 = param_2; (int)puVar2 - (int)param_2 < param_3; puVar2 = puVar2 + 1) {
    uVar1 = dw_uart_getc(iVar3);
    *puVar2 = uVar1;
  }
  return (uint)(-1 < param_3) * param_3;
}

