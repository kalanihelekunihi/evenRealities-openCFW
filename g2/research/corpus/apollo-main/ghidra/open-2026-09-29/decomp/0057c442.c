
int gx8002_read_uart_data(int param_1,uint param_2,undefined2 *param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if (((param_1 == 0) || (param_3 == (undefined2 *)0x0)) || ((param_2 & 0xffff) == 0)) {
    iVar1 = -1;
  }
  else {
    iVar1 = gx8002_uart_read_blocking
                      (param_1,param_2 & 0xffff,param_4,param_4,param_1,param_2,param_3,param_4);
    if (iVar1 < 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0057c61c,DAT_0057c618,DAT_0057ce5c,299,DAT_0057ce58,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0057ce60,DAT_0057ce60,iVar1);
      }
    }
    else {
      *param_3 = (short)iVar1;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0057c61c,DAT_0057c618,DAT_0057ce5c,0x130,DAT_0057ce64,*param_3);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0057ce68,DAT_0057ce68,*param_3);
      }
      FUN_0043dacc(DAT_0057cffc,0x10,param_1,*param_3);
      iVar1 = 0;
    }
  }
  return iVar1;
}

