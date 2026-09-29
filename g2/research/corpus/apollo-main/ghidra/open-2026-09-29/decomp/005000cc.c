
undefined4 FUN_005000cc(undefined4 param_1,undefined1 param_2)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  int iVar3;
  
  puVar1 = DAT_00500308;
  *DAT_00500308 = 1;
  *(undefined4 *)(puVar1 + 4) = param_1;
  puVar1[8] = param_2;
  uVar2 = FUN_004ffef8();
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00500300,DAT_005002fc,DAT_00500338,0xb4,DAT_00500334,param_1,param_2);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_0050033c,DAT_0050033c,param_1,param_2);
  }
  return uVar2;
}

