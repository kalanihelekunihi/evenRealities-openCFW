
undefined8 uart_close(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  pcVar1 = DAT_0058fcbc;
  if (*DAT_0058fcbc == '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x98;
      FUN_0043d574(2,DAT_0058fccc,DAT_0058fcc8,DAT_0058fce0,0x98,DAT_0058fcdc,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0058fce4,DAT_0058fce4);
    }
    uVar3 = 0;
  }
  else {
    iVar2 = FUN_0055e630(3);
    if (iVar2 == 0) {
      *pcVar1 = '\0';
      uVar3 = 0;
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x9e;
        FUN_0043d574(1,DAT_0058fccc,DAT_0058fcc8,DAT_0058fce0,0x9e,DAT_0058fce8,iVar2);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0058fcec,DAT_0058fcec,iVar2);
      }
      uVar3 = 0xffffffff;
    }
  }
  return CONCAT44(param_2,uVar3);
}

