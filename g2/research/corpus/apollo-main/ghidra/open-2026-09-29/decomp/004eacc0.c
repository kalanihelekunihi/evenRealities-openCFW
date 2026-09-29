
undefined8 FUN_004eacc0(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  if (*DAT_004eb744 == 0) {
    uVar1 = 0;
  }
  else if (*DAT_004eb748 < 1) {
    uVar1 = 0;
  }
  else {
    iVar2 = FUN_0044e498(*DAT_004eb744);
    if (iVar2 < 1) {
      uVar1 = 0;
    }
    else {
      uVar1 = 1;
    }
  }
  return CONCAT44(unaff_r7,uVar1);
}

