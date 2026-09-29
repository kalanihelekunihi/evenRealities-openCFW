
undefined4
setting_is_duplicate_message(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  if (param_1 == *DAT_0049bbb0) {
    iVar3 = param_1;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      iVar3 = 0x52;
      param_2 = DAT_0049bbb4;
      param_3 = param_1;
      FUN_0043d574(2,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bbb8,0x52,DAT_0049bbb4,param_1,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0049bdec,DAT_0049bdec,param_1,iVar3,param_2,param_3);
    }
    uVar2 = 1;
  }
  else {
    *DAT_0049bbb0 = param_1;
    uVar2 = 0;
  }
  return uVar2;
}

