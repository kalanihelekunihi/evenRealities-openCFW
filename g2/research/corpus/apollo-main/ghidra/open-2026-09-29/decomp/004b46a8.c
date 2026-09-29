
undefined4 FUN_004b46a8(void)

{
  byte bVar1;
  
  bVar1 = 0;
  while( true ) {
    if (1 < bVar1) {
      return 0;
    }
    if (*(byte *)(DAT_004b46f4 + (uint)bVar1 + 0x57) < 3) break;
    bVar1 = bVar1 + 1;
  }
  return 1;
}

