
undefined4 FUN_0043e2ea(int param_1)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = FUN_0044fa22(0);
  do {
    if (iVar2 == 0) {
      return 0;
    }
    for (uVar3 = 0; uVar3 < *(uint *)(iVar2 + 0x2d4); uVar3 = uVar3 + 1) {
      if (*(int *)(*(int *)(iVar2 + 0x2b8) + uVar3 * 4) == param_1) {
        return 1;
      }
      cVar1 = FUN_0043ee54(*(undefined4 *)(*(int *)(iVar2 + 0x2b8) + uVar3 * 4),param_1);
      if (cVar1 != '\0') {
        return 1;
      }
    }
    iVar2 = FUN_0044fa22(iVar2);
  } while( true );
}

