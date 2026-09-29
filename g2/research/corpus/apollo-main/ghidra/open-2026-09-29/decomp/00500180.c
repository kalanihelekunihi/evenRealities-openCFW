
undefined8 FUN_00500180(undefined4 param_1,undefined4 param_2)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  int iVar3;
  
  puVar1 = DAT_00500308;
  *DAT_00500308 = 4;
  *(undefined4 *)(puVar1 + 4) = param_1;
  uVar2 = FUN_004ffef8();
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    param_2 = 0xde;
    FUN_0043d574(4,DAT_00500300,DAT_005002fc,DAT_00500350,0xde,DAT_0050034c,param_1);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00500354,DAT_00500354,param_1);
  }
  return CONCAT44(param_2,uVar2);
}

