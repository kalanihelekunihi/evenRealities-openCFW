
undefined4 FUN_004eac60(void)

{
  int *piVar1;
  ushort uVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  
  iVar3 = FUN_004e9fd6();
  piVar1 = DAT_004eb744;
  if (iVar3 == 0) {
    uVar4 = 0;
  }
  else if (*DAT_004eb744 == 0) {
    uVar4 = 0;
  }
  else {
    uVar2 = FUN_004e9fd6();
    uVar5 = (uVar2 + 2) / 3;
    if ((uVar5 < 2) || ((int)(uVar5 - 1) <= *DAT_004eb748)) {
      uVar4 = 0;
    }
    else {
      iVar3 = FUN_0044e4bc(*piVar1);
      if (iVar3 < 1) {
        uVar4 = 0;
      }
      else {
        uVar4 = 1;
      }
    }
  }
  return uVar4;
}

