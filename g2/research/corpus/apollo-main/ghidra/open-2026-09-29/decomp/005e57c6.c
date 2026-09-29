
longlong FUN_005e57c6(void)

{
  int *piVar1;
  uint in_r3;
  
  piVar1 = DAT_005e5dd8;
  FUN_005e4c84(0);
  if ((((piVar1[0x73] != 0) && (piVar1[0x74] != 0)) && (piVar1[0x75] != 0)) && (piVar1[0x77] != 0))
  {
    FUN_0043dfa4(piVar1[0x73],1);
    FUN_005ea30c();
    FUN_005e47fe(piVar1[0x74],DAT_005e6254);
    FUN_0049942e(piVar1[0x75],DAT_005e6258);
    FUN_0049942e(piVar1[0x77],DAT_005e6534);
    FUN_005e4894();
  }
  if (*piVar1 != 0) {
    FUN_0043dfa4(*piVar1,1);
  }
  return (ulonglong)in_r3 << 0x20;
}

