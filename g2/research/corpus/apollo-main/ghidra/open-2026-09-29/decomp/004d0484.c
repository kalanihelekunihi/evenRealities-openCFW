
undefined8 FUN_004d0484(undefined4 param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  int local_18;
  undefined4 local_14;
  
  local_18 = 0;
  local_14 = 0;
  iVar2 = 0;
  if ((param_2 != 0) && (FUN_004cff9a(param_2,&local_18,&local_14), local_18 < 0x18)) {
    iVar2 = FUN_004cffc2(param_1,&local_18,&local_14);
  }
  if (iVar2 != 0) {
    uVar1 = FUN_004cfd70(iVar2);
    if (uVar1 < param_2) {
      FUN_004d09b4(DAT_004d0980,DAT_004d06ac,0x309);
    }
    FUN_004d003a(param_1,iVar2,local_18,local_14);
  }
  return CONCAT44(local_18,iVar2);
}

