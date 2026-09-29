
undefined4 even_ai_layout_cache_update(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  int *piVar4;
  
  iVar1 = DAT_004e6558;
  iVar2 = DAT_004e64a8;
  *(undefined1 *)(DAT_004e6558 + 1) = *(undefined1 *)(DAT_004e64a8 + 0x18);
  piVar4 = *(int **)(iVar2 + 0x14);
  if (piVar4 == (int *)0x0) {
    *(undefined1 *)(iVar1 + 0xc) = 0;
    *(undefined1 *)(iVar1 + 0xd) = 0;
  }
  else {
    if ((*piVar4 == 0) || (iVar2 = FUN_0043e2ea(*piVar4), iVar2 == 0)) {
      *(undefined1 *)(iVar1 + 0xc) = 0;
    }
    else {
      *(undefined1 *)(iVar1 + 0xc) = 1;
      uVar3 = FUN_0043fdda(*piVar4);
      *(undefined4 *)(iVar1 + 4) = uVar3;
    }
    if ((piVar4[1] == 0) || (iVar2 = FUN_0043e2ea(piVar4[1]), iVar2 == 0)) {
      *(undefined1 *)(iVar1 + 0xd) = 0;
    }
    else {
      *(undefined1 *)(iVar1 + 0xd) = 1;
      uVar3 = FUN_0043fdda(piVar4[1]);
      *(undefined4 *)(iVar1 + 8) = uVar3;
    }
  }
  return in_r3;
}

