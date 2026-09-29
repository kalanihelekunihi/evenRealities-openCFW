
undefined4 FUN_004dcd32(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  if (param_1 < 0x10) {
    uVar1 = *(undefined4 *)(DAT_004dd464 + param_1 * 4);
  }
  else {
    uVar3 = param_1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = 0x9b;
      param_2 = DAT_004dd468;
      param_3 = param_1;
      FUN_0043d574(2,DAT_004dd474,DAT_004dd470,DAT_004dd46c,0x9b,DAT_004dd468,param_1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004dd478,DAT_004dd478,param_1,uVar3,param_2,param_3);
    }
    uVar1 = 0xffffff;
  }
  return uVar1;
}

