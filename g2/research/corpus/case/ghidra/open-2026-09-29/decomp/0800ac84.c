
void FUN_0800ac84(void)

{
  int *piVar1;
  int iVar2;
  
  FUN_0800bffc();
  piVar1 = DAT_0800acc8;
  if (*DAT_0800acc8 == 0) {
    FUN_0800bf94(DAT_0800accc);
    FUN_0800bf94(DAT_0800acd0);
    iVar2 = DAT_0800accc;
    piVar1[3] = DAT_0800accc;
    piVar1[4] = iVar2 + 0x14;
    iVar2 = FUN_0800c5d0(10,0x10,DAT_0800acd8,DAT_0800acd4,0);
    *piVar1 = iVar2;
    if (iVar2 != 0) {
      FUN_0800c0b8(iVar2,&LAB_0800acdc);
    }
  }
  FUN_0800c014();
  return;
}

