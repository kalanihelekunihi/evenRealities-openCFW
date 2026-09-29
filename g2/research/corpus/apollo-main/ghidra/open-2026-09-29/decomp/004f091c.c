
undefined4 FUN_004f091c(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  uint *puVar1;
  int iVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_004f0cb0;
  *DAT_004f0cb0 = param_1;
  *DAT_004f0cac = 1;
  if (*puVar1 < 6) {
    FUN_004efffc();
    *DAT_004f153c = 0;
    uVar3 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = *puVar1;
      param_1 = 0x1b0;
      param_2 = DAT_004f1394;
      FUN_0043d574(1,DAT_004f0e0c,DAT_004f0e08,DAT_004f1398,0x1b0,DAT_004f1394,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004f139c,DAT_004f139c,*puVar1,param_1,param_2,param_3);
    }
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

