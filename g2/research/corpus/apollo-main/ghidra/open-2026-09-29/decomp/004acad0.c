
undefined8 FUN_004acad0(void)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  undefined4 unaff_r7;
  
  if (*DAT_004acb00 == '\0') {
    iVar3 = FUN_004acac0();
    if ((iVar3 == 1) || (iVar3 = FUN_004acab4(), iVar3 == 1)) {
      bVar1 = 1;
    }
    else {
      bVar1 = 0;
    }
    uVar2 = (uint)bVar1;
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(unaff_r7,uVar2);
}

