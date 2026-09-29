
undefined8 hal_i2c_power_up(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = DAT_00504764;
  iVar4 = DAT_00504760;
  iVar3 = 0;
  if (param_1 == 4) {
    FUN_00480f0c(**(undefined4 **)(DAT_00504760 + 0x48),*DAT_00504764);
    FUN_00480f0c(*(undefined4 *)(*(int *)(iVar4 + 0x48) + 4),*puVar1);
  }
  iVar4 = 0;
  while ((iVar4 < 1000 &&
         (iVar3 = FUN_0055c7e8(*(undefined4 *)(DAT_00504760 + (uint)param_1 * 0x10 + 4),2,1),
         iVar3 != 0))) {
    FUN_004910f4(10);
    iVar4 = iVar4 + 1;
  }
  if (iVar3 == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = 4;
  }
  return CONCAT44(param_4,uVar2);
}

