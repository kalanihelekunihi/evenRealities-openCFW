
undefined4 FUN_005ea7dc(void)

{
  int iVar1;
  undefined4 in_r3;
  uint uVar2;
  
  iVar1 = DAT_005eb28c;
  for (uVar2 = 0; uVar2 < 0xc; uVar2 = uVar2 + 1) {
    if (*(int *)(iVar1 + uVar2 * 4 + 0xc) != 0) {
      FUN_0043ded4(*(undefined4 *)(iVar1 + uVar2 * 4 + 0xc),1);
    }
  }
  *(undefined2 *)(iVar1 + 0x1c0) = 0;
  *(undefined1 *)(iVar1 + 0x1c2) = 0;
  return in_r3;
}

