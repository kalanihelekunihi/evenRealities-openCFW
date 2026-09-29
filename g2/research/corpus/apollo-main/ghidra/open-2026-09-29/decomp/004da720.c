
undefined4 FUN_004da720(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_14 [2];
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_1 == 1) {
    HUB_Open(5);
    local_14[0] = param_2;
    HUB_ParameterConfig(5,local_14);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004da818,DAT_004da814,DAT_004da824,0x202,DAT_004da820,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004da828,DAT_004da828,param_2);
    }
  }
  else {
    HUB_Close(5);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004da818,DAT_004da814,DAT_004da824,0x205,DAT_004da82c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004da830,DAT_004da830);
    }
  }
  return 0;
}

