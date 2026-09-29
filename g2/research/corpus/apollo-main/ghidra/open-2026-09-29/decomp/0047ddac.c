
undefined4 FUN_0047ddac(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = FUN_00443484();
  if (iVar1 == 0) {
    iVar1 = FUN_0048eb90();
    if ((iVar1 != 0) && (*DAT_0047e290 < 10)) {
      *DAT_0047e290 = *DAT_0047e290 + 1;
      unaff_r7 = 0;
      FUN_0047e7b0(*DAT_0047e28c,4,5000,0);
    }
  }
  else {
    unaff_r7 = 0;
    FUN_0047e7b0(*DAT_0047e28c,4,2000,0);
  }
  return unaff_r7;
}

