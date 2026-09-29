
undefined8 FUN_005eb4f6(void)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 in_r3;
  
  iVar5 = DAT_005ebc34;
  bVar1 = FUN_005eb30c();
  if (((*(int *)(iVar5 + 0x214) == 0) || (*(int *)(iVar5 + 0x21c) == 0)) || (bVar1 < 2)) {
    iVar2 = 0;
  }
  else {
    iVar2 = FUN_0044dce2(*(undefined4 *)(iVar5 + 0x21c),1);
    if (iVar2 == 0) {
      iVar2 = 0;
    }
    else {
      iVar3 = FUN_005eb438(iVar5);
      iVar4 = FUN_0043fce0(*(undefined4 *)(iVar5 + 0x21c));
      iVar2 = FUN_0043fce0(iVar2);
      iVar2 = ((iVar2 + iVar4) - iVar3) + 1;
      if (iVar2 < 0) {
        iVar2 = 0;
      }
      iVar3 = FUN_0044e498(*(undefined4 *)(iVar5 + 0x214));
      iVar5 = FUN_0044e4bc(*(undefined4 *)(iVar5 + 0x214));
      iVar5 = iVar5 + iVar3;
      if (iVar5 < 0) {
        iVar5 = 0;
      }
      if (iVar5 < iVar2) {
        iVar2 = iVar5;
      }
    }
  }
  return CONCAT44(in_r3,iVar2);
}

