
undefined4
terminal_message_session_matches(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = td_counter_b_get();
  if (param_1 == iVar1) {
    uVar2 = 1;
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      iVar3 = DAT_005e8c08;
      if (param_2 != 0) {
        iVar3 = param_2;
      }
      FUN_0043d574(2,DAT_005e8c18,DAT_005e8c14,DAT_005e8c10,0x2d,DAT_005e8c0c,iVar3,param_1,iVar1,
                   param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      if (param_2 == 0) {
        param_2 = DAT_005e8c08;
      }
      compress_log_output(0x8c00000,DAT_005e8e34,DAT_005e8e34,param_2,param_1,iVar1);
    }
    uVar2 = 0;
  }
  return uVar2;
}

