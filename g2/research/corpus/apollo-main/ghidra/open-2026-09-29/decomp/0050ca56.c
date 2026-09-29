
undefined4
ui_onboarding_stock_sub_0050CA56(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  ushort *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_0050d548;
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0050d558,DAT_0050d554,DAT_0050d550,0xbb,DAT_0050d54c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0050d55c);
    }
    uVar3 = 0;
  }
  else if ((param_2 & 0xffff) < (uint)*DAT_0050d548) {
    FUN_00439be4(param_1,DAT_0050d544 + (param_2 & 0xffff) * 0x380,0x380,param_4,param_1,param_2,
                 param_3,param_4);
    uVar3 = 1;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0050d558,DAT_0050d554,DAT_0050d550,0xc0,DAT_0050d560,param_2 & 0xffff,
                   *puVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8800000,DAT_0050d564,DAT_0050d564,param_2 & 0xffff,*puVar1);
    }
    uVar3 = 0;
  }
  return uVar3;
}

