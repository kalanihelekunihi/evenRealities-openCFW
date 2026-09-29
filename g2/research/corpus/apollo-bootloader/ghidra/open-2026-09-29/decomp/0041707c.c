
undefined8 FUN_0041707c(undefined4 param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  int local_18;
  undefined4 local_14;
  
  local_18 = 0;
  local_14 = 0;
  iVar2 = 0;
  if ((param_2 != 0) && (FUN_00416c26(param_2,&local_18,&local_14), local_18 < 0x18)) {
    iVar2 = FUN_00416c4e(param_1,&local_18,&local_14);
  }
  if (iVar2 != 0) {
    uVar1 = FUN_004169fc(iVar2);
    if (uVar1 < param_2) {
      FUN_00415734(DAT_00417320,DAT_00417200,0x309);
    }
    FUN_00416cc6(param_1,iVar2,local_18,local_14);
  }
  return CONCAT44(local_18,iVar2);
}

