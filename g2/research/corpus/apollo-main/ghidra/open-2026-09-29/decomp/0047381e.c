
undefined4 FUN_0047381e(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  uVar1 = DAT_00473910;
  if (*DAT_0047390c == 0) {
    FUN_0044d25c(3,DAT_004738f0,0x124,DAT_00473914);
    unaff_r7 = uVar1;
  }
  else {
    iVar2 = FUN_00441c44(*DAT_0047390c,1000);
    uVar1 = DAT_00473918;
    if (iVar2 == 0) {
      FUN_0044d25c(3,DAT_004738f0,0x12a,DAT_00473914);
      unaff_r7 = uVar1;
    }
  }
  return unaff_r7;
}

