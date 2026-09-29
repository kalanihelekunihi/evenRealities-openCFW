
undefined8 FUN_004425a6(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar1 = DAT_00442d14;
  uVar3 = DAT_00442d18 - DAT_00442d14 >> 4;
  if (0x80 < uVar3) {
    uVar3 = 0x80;
  }
  *DAT_00442cd4 = uVar3;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_1 = 0xab;
    param_2 = DAT_00442d1c;
    param_3 = uVar3;
    FUN_0043d574(4,DAT_00442cf4,DAT_00442cf0,DAT_00442d20,0xab,DAT_00442d1c,uVar3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00442d24,DAT_00442d24,uVar3,param_1,param_2,param_3);
  }
  FUN_00439be4(DAT_00442cd8,iVar1,uVar3 << 4);
  return CONCAT44(param_2,param_1);
}

