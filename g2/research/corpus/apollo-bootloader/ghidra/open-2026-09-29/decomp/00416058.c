
undefined8 FUN_00416058(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  iVar1 = FUN_0041602a();
  if (iVar1 == 0) {
    iVar1 = FUN_00418b56();
    if ((iVar1 == 1) && (*DAT_0041658c == 0)) {
      *DAT_0041658c = 1;
      uVar2 = 0;
    }
    else {
      uVar2 = 0xffffffff;
    }
  }
  else {
    uVar2 = 0xfffffffa;
  }
  return CONCAT44(unaff_r7,uVar2);
}

