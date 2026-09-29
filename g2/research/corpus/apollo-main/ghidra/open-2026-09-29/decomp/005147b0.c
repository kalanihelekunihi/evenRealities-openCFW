
void FUN_005147b0(int param_1)

{
  int iVar1;
  uint *puVar2;
  uint uVar3;
  uint uVar4;
  uint *puVar5;
  bool bVar6;
  
  if (param_1 == 0) {
    FUN_004b127c(0x2000);
    return;
  }
  iVar1 = *(int *)(param_1 + 0x14);
  if ((int)((uint)*(byte *)(param_1 + 0x18) << 0x1a) < 0) {
    if (iVar1 == *(int *)(param_1 + 0x2c) * (iVar1 / *(int *)(param_1 + 0x2c))) {
      return;
    }
  }
  else if (iVar1 == 0) {
    return;
  }
  FUN_00514b7c(param_1);
  if ((int)((uint)*(byte *)(param_1 + 0x18) << 0x1a) < 0) {
    puVar5 = (uint *)*DAT_00514b78;
    bVar6 = *(char *)((int)puVar5 + 0xf9) != '\x01';
    uVar4 = 1;
    puVar2 = DAT_00514b78;
    if (bVar6) {
      uVar4 = *(uint *)(param_1 + 0x28);
      puVar5 = (uint *)(uVar4 >> 2);
      puVar2 = *(uint **)(param_1 + 0x30);
    }
    if (bVar6 && puVar2 != puVar5) {
      bVar6 = puVar2 != (uint *)(uVar4 >> 1);
      if (bVar6) {
        puVar5 = (uint *)((int)puVar5 * 3);
      }
      if (bVar6 && puVar2 != puVar5) {
        uVar3 = 0;
        if (puVar2 != (uint *)0x0) {
          uVar3 = *(uint *)(param_1 + 0x34);
          uVar4 = 0xffffff;
        }
        if (puVar2 != (uint *)0x0 && uVar3 != uVar4) goto LAB_0051482c;
      }
    }
    FUN_00523f10(*(undefined4 *)(param_1 + 0x34));
    *(undefined4 *)(param_1 + 0x1c) = *(undefined4 *)(param_1 + 0x34);
  }
  else {
    FUN_00523f10(*(undefined4 *)(param_1 + 0x1c));
  }
LAB_0051482c:
  if (*(int *)(param_1 + 0x1c) == 0xffffff) {
    iVar1 = FUN_00514026();
    if (-1 < iVar1) {
      *(undefined4 *)(param_1 + 0x1c) = 0xffffffff;
    }
  }
  return;
}

