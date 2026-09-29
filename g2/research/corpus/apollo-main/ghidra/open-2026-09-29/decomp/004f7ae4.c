
undefined8 FUN_004f7ae4(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  
  piVar1 = DAT_004f7f14;
  iVar3 = param_1;
  if ((*DAT_004f8094 != 0) && (*DAT_004f7f14 == 0)) {
    if ((param_1 < 0) || ((int)(uint)*DAT_004f7c90 <= param_1)) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        iVar3 = 0xa0a;
        param_2 = DAT_004f84c0;
        param_3 = param_1;
        FUN_0043d574(2,DAT_004f81e0,DAT_004f81dc,DAT_004f84c4,0xa0a,DAT_004f84c0,param_1,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004f84c8,DAT_004f84c8,param_1,iVar3,param_2,param_3);
      }
    }
    else {
      *DAT_004f81d8 = 1;
      *piVar1 = 1;
      *DAT_004f81e4 = param_1;
      FUN_004f7634(0,100,DAT_004f8614);
      FUN_004f76b6(0x20,0xfa);
      iVar3 = param_1;
    }
  }
  return CONCAT44(param_2,iVar3);
}

