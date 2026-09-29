
undefined4 FUN_004215ae(byte param_1)

{
  byte bVar1;
  
  bVar1 = 0;
  while( true ) {
    if (1 < bVar1) {
      return 0;
    }
    if (*(int *)(DAT_00422210 + (uint)param_1 * 8 + (uint)bVar1 * 4) != 0) break;
    bVar1 = bVar1 + 1;
  }
  return 1;
}

