
undefined8 FUN_00416ad0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_004169fc(param_1);
  uVar2 = FUN_00416a9c(param_1);
  uVar2 = FUN_00416aa6(uVar2,iVar1 - *DAT_00417204);
  iVar1 = FUN_00416a2c(param_1);
  if (iVar1 != 0) {
    FUN_00415734(DAT_00417238,DAT_00417200,0x1ba);
  }
  return CONCAT44(param_4,uVar2);
}

