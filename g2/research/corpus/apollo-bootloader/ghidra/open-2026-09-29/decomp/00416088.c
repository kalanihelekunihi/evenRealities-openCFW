
undefined8 FUN_00416088(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  iVar1 = FUN_00418b56();
  if (iVar1 == 0) {
    uVar2 = 3;
  }
  else if (iVar1 == 2) {
    uVar2 = 2;
  }
  else if (*DAT_0041658c == 1) {
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(unaff_r7,uVar2);
}

