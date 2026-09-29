
undefined1 FUN_004894a4(uint param_1)

{
  byte bVar1;
  
  bVar1 = 0;
  while( true ) {
    if (*(char *)(DAT_00489e94 + (uint)bVar1) == '\0') {
      return 0;
    }
    if (param_1 == *(byte *)(DAT_00489e94 + (uint)bVar1)) break;
    bVar1 = bVar1 + 1;
  }
  return 1;
}

