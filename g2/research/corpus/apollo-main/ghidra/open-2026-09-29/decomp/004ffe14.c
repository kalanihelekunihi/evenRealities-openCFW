
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_004ffe14(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = *_DAT_005002f0;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_1 = 0x23;
    param_2 = _DAT_005002f4;
    param_3 = uVar2;
    FUN_0043d574(4,DAT_00500300,DAT_005002fc,_DAT_005002f8,0x23,_DAT_005002f4,uVar2,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,_DAT_00500304,_DAT_00500304,uVar2,param_1,param_2,param_3);
  }
  FUN_0043c0e4(DAT_00500308,0x3c,0);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_1 = 0x27;
    param_2 = _DAT_0050030c;
    FUN_0043d574(4,DAT_00500300,DAT_005002fc,_DAT_005002f8);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,_DAT_00500310,_DAT_00500310);
  }
  return CONCAT44(param_2,param_1);
}

