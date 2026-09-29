
undefined8 uart_init(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  pcVar1 = DAT_0058fcb0;
  if (*DAT_0058fcb0 == '\0') {
    FUN_00598160(DAT_0058fcac,DAT_0058fcb4,0x40,param_4,param_2,param_3,param_4);
    FUN_0055e8f0(3,DAT_0058fcb8);
    *pcVar1 = '\x01';
  }
  pcVar1 = DAT_0058fcbc;
  if (*DAT_0058fcbc == '\0') {
    iVar2 = FUN_0055e5bc(3);
    if (iVar2 == 0) {
      *pcVar1 = '\x01';
      uVar3 = 0;
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x88;
        FUN_0043d574(1,DAT_0058fccc,DAT_0058fcc8,DAT_0058fcc4,0x88,DAT_0058fcd4,iVar2);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0058fcd8,DAT_0058fcd8,iVar2);
      }
      uVar3 = 0xffffffff;
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x82;
      FUN_0043d574(2,DAT_0058fccc,DAT_0058fcc8,DAT_0058fcc4,0x82,DAT_0058fcc0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0058fcd0);
    }
    uVar3 = 0;
  }
  return CONCAT44(param_2,uVar3);
}

