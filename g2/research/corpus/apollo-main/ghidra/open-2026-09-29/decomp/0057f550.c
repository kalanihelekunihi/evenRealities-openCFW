
undefined4 FUN_0057f550(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint local_24;
  uint local_20;
  int local_1c;
  int local_18;
  
  if (*DAT_0057ffa8 == 0) {
    FUN_004733ee(DAT_0057ffac);
  }
  else {
    iVar1 = FUN_004d0716(*DAT_0057ffa8);
    if (iVar1 == 0) {
      FUN_004733ee(DAT_0057ffb0);
    }
    else {
      FUN_0043c0e4(&local_24,0x10,0);
      FUN_004d0580(iVar1,DAT_0057ffb4,&local_24);
      uVar2 = local_24 + local_20;
      iVar1 = FUN_004d05fa();
      if (uVar2 == 0) {
        uVar3 = 0;
      }
      else {
        uVar3 = (local_20 * 100) / uVar2;
      }
      FUN_004733ee(DAT_0057ffb8);
      FUN_004733ee(DAT_0057ffbc,uVar2 >> 10,local_20 >> 10,local_24 >> 10,local_24 >> 10);
      FUN_004733ee(DAT_0057ffc0);
      FUN_004733ee(DAT_0057ffc4,0x1c2,0x70800);
      FUN_004733ee(DAT_0057ffc8,iVar1 + 0xc74);
      FUN_004733ee(DAT_0057ffcc,uVar2 >> 10,uVar2);
      FUN_004733ee(DAT_0057ffd0,local_20 >> 10,local_20);
      FUN_004733ee(DAT_0057ffd4,local_24 >> 10,local_24);
      FUN_004733ee(DAT_0057ffd8,uVar3);
      FUN_004733ee(DAT_0057ffdc,local_1c);
      FUN_004733ee(DAT_0057ffe0,local_18);
      FUN_004733ee(DAT_0057ffe4,local_1c - local_18);
      FUN_004733ee(DAT_0057ffe8);
      if ((int)uVar3 < 0x5b) {
        if (0x4b < (int)uVar3) {
          FUN_004733ee(PTR_s_CAUTION__Memory_usage_is_high__>_0057fff0);
        }
      }
      else {
        FUN_004733ee(DAT_0057ffec);
      }
    }
  }
  return 0;
}

