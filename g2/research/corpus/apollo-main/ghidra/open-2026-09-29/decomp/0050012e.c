
undefined8 FUN_0050012e(undefined4 param_1,undefined4 param_2)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  int iVar3;
  
  puVar1 = DAT_00500308;
  *DAT_00500308 = 3;
  *(undefined4 *)(puVar1 + 4) = param_1;
  uVar2 = FUN_004ffef8();
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    param_2 = 0xd0;
    FUN_0043d574(4,DAT_00500300,DAT_005002fc,DAT_00500344,0xd0,DAT_00500340,param_1);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00500348,DAT_00500348,param_1);
  }
  return CONCAT44(param_2,uVar2);
}

