
undefined8 FUN_004b8140(uint param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  int iVar1;
  undefined *puVar2;
  uint uVar3;
  
  uVar3 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = DAT_004b87a4;
    if ((param_1 & 0xff) == 3) {
      param_3 = &DAT_004b8374;
    }
    uVar3 = 0x38c;
    param_2 = DAT_004b87a8;
    FUN_0043d574(4,DAT_004b8210,DAT_004b820c,DAT_004b87ac,0x38c,DAT_004b87a8,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    puVar2 = DAT_004b87a4;
    if ((param_1 & 0xff) == 3) {
      puVar2 = &DAT_004b8374;
    }
    compress_log_output(0x10400000,DAT_004b87b0,DAT_004b87b0,puVar2,uVar3,param_2,param_3);
  }
  *DAT_004b8730 = (char)param_1;
  return CONCAT44(param_2,uVar3);
}

