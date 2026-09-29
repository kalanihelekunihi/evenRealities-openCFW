
undefined8 FUN_0045ecca(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *param_1;
  iVar1 = *(int *)(iVar2 + 0x10);
  *(undefined1 *)(iVar1 + 0x1c) = 1;
  iVar2 = FUN_0045fcd2(iVar2);
  if (*(int *)(iVar1 + 0x18) != 0) {
    (**(code **)(iVar1 + 0x18))(iVar1,iVar2,0x4d,0,param_2,param_3,param_4);
  }
  FUN_0045bbd2();
  if (iVar2 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x55;
      param_3 = DAT_0045f67c;
      FUN_0043d574(2,DAT_0045f688,DAT_0045f684,DAT_0045f680);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0045f68c,DAT_0045f68c);
    }
  }
  else {
    *(undefined1 *)(iVar2 + 0xe8) = 0;
    FUN_0045fd06(iVar2);
  }
  return CONCAT44(param_3,param_2);
}

