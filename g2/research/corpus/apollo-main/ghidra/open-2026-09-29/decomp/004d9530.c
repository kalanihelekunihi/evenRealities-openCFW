
void SVC_KvdbRunMigrations(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  iVar1 = DAT_004d9aa0;
  uVar2 = DAT_004d9a9c - DAT_004d9a98 >> 2;
  if (100 < uVar2) {
    uVar2 = 100;
  }
  FUN_00439be4(DAT_004d9aa0,DAT_004d9a98,uVar2 << 2);
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1) {
    if (*(int *)(iVar1 + uVar3 * 4) != 0) {
      (**(code **)(iVar1 + uVar3 * 4))();
    }
  }
  return;
}

