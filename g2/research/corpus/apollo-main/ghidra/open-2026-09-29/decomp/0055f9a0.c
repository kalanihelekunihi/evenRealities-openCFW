
undefined4 FUN_0055f9a0(void)

{
  byte bVar1;
  undefined4 uVar2;
  
  if (!NAN(*(float *)(DAT_0055f9dc + 0x10))) {
    bVar1 = *DAT_0055f9dc;
    if (bVar1 < 4) {
      if (1 < bVar1) {
        uVar2 = FUN_0058eac4(DAT_0055f9e0,1,*(undefined4 *)(DAT_0055f9e0 + 0xe0));
        return uVar2;
      }
    }
    else if (bVar1 == 4) {
      uVar2 = FUN_0058eac4(DAT_0055f9e0,0,*(undefined4 *)(DAT_0055f9e0 + 0xe0));
      return uVar2;
    }
  }
  return DAT_0055f9e4;
}

