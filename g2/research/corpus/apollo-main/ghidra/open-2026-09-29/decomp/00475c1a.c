
/* WARNING: Removing unreachable block (ram,0x00475c78) */
/* WARNING: Removing unreachable block (ram,0x00475c80) */
/* WARNING: Removing unreachable block (ram,0x00475c9a) */
/* WARNING: Removing unreachable block (ram,0x00475ca2) */
/* WARNING: Removing unreachable block (ram,0x00475caa) */
/* WARNING: Removing unreachable block (ram,0x00475cb6) */

undefined8 Thread_MsgPbNotifyByBle(undefined1 param_1,uint param_2,uint param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = param_2;
  uVar4 = param_4;
  iVar1 = semantic_OtaTransferActive();
  if (iVar1 == 0) {
    iVar1 = APP_IsLeftSlaveRole();
    if (iVar1 == 0) {
      iVar1 = APP_IsLocalSlaveAsCmdRole();
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        param_3 = uVar3;
        if (iVar1 << 0x1e < 0) {
          param_3 = 0x1d5;
          FUN_0043d574(4,DAT_00475d6c,DAT_00475d68,DAT_00475f7c,0x1d5,DAT_00475f8c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_00475f90,DAT_00475f90);
        }
        uVar2 = 8;
      }
      else {
        uVar2 = Thread_MsgTxByBle(0,1,param_1,param_2 & 0xff,param_3,param_4 & 0xffff,uVar4);
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      param_3 = uVar3;
      if (iVar1 << 0x1e < 0) {
        param_3 = 0x1d0;
        FUN_0043d574(4,DAT_00475d6c,DAT_00475d68,DAT_00475f7c,0x1d0,DAT_00475f84);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00475f88,DAT_00475f88);
      }
      uVar2 = 8;
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    param_3 = uVar3;
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x1c4;
      FUN_0043d574(4,DAT_00475d6c,DAT_00475d68,DAT_00475f7c,0x1c4,DAT_00475f78);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00475f80,DAT_00475f80);
    }
    uVar2 = 0;
  }
  return CONCAT44(param_3,uVar2);
}

