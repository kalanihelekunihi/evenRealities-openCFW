
undefined8 FUN_0046d1c6(int param_1,uint param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = param_2;
  if (((param_1 != 0) && (uVar2 = param_2 & 0xff, uVar2 != 0)) && (uVar2 != 2)) {
    if (uVar2 < 2) {
      FUN_004b1ef6();
      uVar3 = param_2;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_3 = param_2 & 0xff;
        param_1 = 0x17a;
        uVar3 = DAT_0046d600;
        FUN_0043d574(2,DAT_0046d580,DAT_0046d57c,DAT_0046d604,0x17a,DAT_0046d600,param_3,param_4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0046d608,DAT_0046d608,param_2 & 0xff,param_1,uVar3,param_3
                           );
      }
    }
  }
  return CONCAT44(uVar3,param_1);
}

