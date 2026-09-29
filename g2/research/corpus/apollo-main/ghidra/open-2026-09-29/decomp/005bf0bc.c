
void FUN_005bf0bc(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  iVar1 = DAT_005bf10c;
  uVar2 = DAT_005bf108 - DAT_005bf104 >> 3;
  if (0x100 < uVar2) {
    uVar2 = 0x100;
  }
  FUN_00439be4(DAT_005bf10c,DAT_005bf104,uVar2 << 3);
  FUN_00567c4c(iVar1,uVar2,8,DAT_005bf110);
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1) {
    if (*(int *)(iVar1 + uVar3 * 8) != 0) {
      (**(code **)(iVar1 + uVar3 * 8))();
    }
  }
  return;
}

