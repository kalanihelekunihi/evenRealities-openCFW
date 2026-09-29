
longlong FUN_004e83c8(uint param_1)

{
  byte bVar1;
  uint unaff_r7;
  
  if (param_1 < 5) {
    bVar1 = *(byte *)(DAT_004e8bc4 + param_1);
    if (bVar1 == 0) {
      FUN_004f4670(*DAT_004e8db4);
    }
    else if (bVar1 == 2) {
      FUN_004ef9a4(*DAT_004e8db4);
    }
    else if (bVar1 < 2) {
      FUN_004ebdfc(*DAT_004e8db4);
    }
    else if (bVar1 == 4) {
      FUN_004faf9c(*DAT_004e8db4);
    }
    else if (bVar1 < 4) {
      FUN_004fd7b0(*DAT_004e8db4);
    }
  }
  return (ulonglong)unaff_r7 << 0x20;
}

