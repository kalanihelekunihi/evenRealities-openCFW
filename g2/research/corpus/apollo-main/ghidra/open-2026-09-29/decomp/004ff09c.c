
int FUN_004ff09c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint local_214;
  undefined1 auStack_210 [512];
  undefined4 uStack_10;
  
  local_214 = 0x200;
  uStack_10 = param_4;
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ff4a8,DAT_004ff4a4,DAT_004ff4b4,0x44f,DAT_004ff4b0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ff4b8,DAT_004ff4b8);
    }
    iVar1 = 1;
  }
  else {
    FUN_0043c0e4(auStack_210,0x200,0);
    iVar1 = FUN_004fef04(param_1,auStack_210,&local_214);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004ff4a8,DAT_004ff4a4,DAT_004ff4b4,0x458,DAT_004ff49c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004ff4ac,DAT_004ff4ac);
      }
      iVar1 = 2;
    }
    else {
      iVar1 = Thread_MsgPbNotifyByBle(1,1,auStack_210,local_214 & 0xffff);
      if (iVar1 == 0) {
        iVar1 = 0;
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004ff4a8,DAT_004ff4a4,DAT_004ff4b4,0x460,DAT_004ff4bc,iVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_004ff7d8,DAT_004ff7d8,iVar1);
        }
      }
    }
  }
  return iVar1;
}

