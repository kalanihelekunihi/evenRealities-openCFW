
undefined4 FUN_00592484(int param_1,uint param_2)

{
  int iVar1;
  uint *puVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar4 = *(int *)(param_1 + 8);
  if ((int)(param_2 << 0x1e) < 0) {
    FUN_0059243e(param_1);
  }
  iVar1 = DAT_00592640;
  if ((int)(param_2 << 0x1c) < 0) {
    if (*(int *)(DAT_00592640 + iVar4 * 0x1000 + 0x158) << 0x1f < 0) {
      puVar2 = (uint *)(DAT_00592640 + iVar4 * 0x1000 + 0x158);
      *puVar2 = *puVar2 & 0xfffffffd;
    }
    else {
      puVar2 = (uint *)(DAT_00592640 + iVar4 * 0x1000 + 0x108);
      *puVar2 = *puVar2 | 1;
      FUN_00592556(param_1,1);
      *(undefined1 *)(param_1 + 0x1e) = 1;
    }
    if (*(int *)(param_1 + 0x10) != -1) {
      if (*(int *)(iVar1 + iVar4 * 0x1000 + 0x168) != 0) {
        return 9;
      }
      if (*(int *)(param_1 + 0x14) == *(int *)(param_1 + 0x10)) {
        uVar3 = *(undefined4 *)(param_1 + 0xc);
      }
      else {
        uVar3 = *(undefined4 *)(param_1 + 0x10);
      }
      *(undefined4 *)(param_1 + 0x14) = uVar3;
      *(undefined4 *)(iVar1 + iVar4 * 0x1000 + 0x160) = uVar3;
      *(undefined4 *)(iVar1 + iVar4 * 0x1000 + 0x164) = *(undefined4 *)(param_1 + 0x18);
      *(undefined4 *)(iVar1 + iVar4 * 0x1000 + 0x168) = 1;
    }
  }
  if (((param_2 & 9) == 1) && (*(char *)(param_1 + 0x1e) != '\0')) {
    FUN_00592584(param_1,1);
    puVar2 = (uint *)(DAT_00592640 + iVar4 * 0x1000 + 0x158);
    *puVar2 = *puVar2 & 0xfffffffd;
    *(undefined1 *)(param_1 + 0x1e) = 0;
  }
  return 0;
}

