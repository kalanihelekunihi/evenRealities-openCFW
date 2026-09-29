
undefined4 FUN_0048fce2(int param_1)

{
  byte bVar1;
  int iVar2;
  bool bVar3;
  int iVar4;
  undefined1 auStack_58 [40];
  undefined1 auStack_30 [40];
  
  bVar1 = *(byte *)(param_1 + 0x16);
  if ((bVar1 & 0xf) == 10) {
    for (iVar4 = **(int **)(param_1 + 0x1c); iVar4 != 0; iVar4 = *(int *)(iVar4 + 8)) {
      iVar2 = FUN_004d93a4(auStack_30,iVar4);
      if (iVar2 != 0) {
        *(undefined1 *)(iVar4 + 0xc) = 0;
        iVar2 = FUN_0048fdf2(auStack_30);
        if (iVar2 == 0) {
          return 0;
        }
      }
    }
  }
  else if ((bVar1 & 0xc0) == 0) {
    bVar3 = true;
    if (((bVar1 & 0x30) == 0x10) && (*(int *)(param_1 + 0x20) != 0)) {
      **(undefined1 **)(param_1 + 0x20) = 0;
    }
    else if (((bVar1 & 0x30) == 0x20) || ((bVar1 & 0x30) == 0x30)) {
      **(undefined2 **)(param_1 + 0x20) = 0;
      bVar3 = false;
    }
    if (bVar3) {
      if ((((*(byte *)(param_1 + 0x16) & 0xf) == 8) || ((*(byte *)(param_1 + 0x16) & 0xf) == 9)) &&
         ((*(int *)(*(int *)(param_1 + 0x24) + 8) != 0 ||
          ((*(int *)(*(int *)(param_1 + 0x24) + 0xc) != 0 ||
           (**(int **)(*(int *)(param_1 + 0x24) + 4) != 0)))))) {
        iVar4 = FUN_004d9384(auStack_58,*(undefined4 *)(param_1 + 0x24),
                             *(undefined4 *)(param_1 + 0x1c));
        if ((iVar4 != 0) && (iVar4 = FUN_0048fdf2(auStack_58), iVar4 == 0)) {
          return 0;
        }
      }
      else {
        FUN_0043c0e4(*(undefined4 *)(param_1 + 0x1c),*(undefined2 *)(param_1 + 0x12),0);
      }
    }
  }
  else if (((bVar1 & 0xc0) == 0x80) &&
          ((**(undefined4 **)(param_1 + 0x18) = 0, (bVar1 & 0x30) == 0x20 ||
           ((bVar1 & 0x30) == 0x30)))) {
    **(undefined2 **)(param_1 + 0x20) = 0;
  }
  return 1;
}

