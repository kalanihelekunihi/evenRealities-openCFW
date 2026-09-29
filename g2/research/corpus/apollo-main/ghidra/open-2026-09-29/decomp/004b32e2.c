
undefined4 FUN_004b32e2(byte param_1,int param_2)

{
  byte bVar1;
  byte bVar2;
  
  bVar1 = 0;
  do {
    if (param_1 <= bVar1) {
      return 0;
    }
    for (bVar2 = 0; bVar2 < 2; bVar2 = bVar2 + 1) {
      if ((*(byte *)(param_2 + (uint)bVar1) == bVar2) &&
         (((*(char *)((uint)bVar2 + DAT_004b3c8c + 0x59) == '\0' ||
           (*(char *)((uint)bVar2 + DAT_004b3c8c + 0x59) == '\x04')) ||
          (*(char *)((uint)bVar2 + DAT_004b3c8c + 0x59) == '\x05')))) {
        return 1;
      }
    }
    bVar1 = bVar1 + 1;
  } while( true );
}

