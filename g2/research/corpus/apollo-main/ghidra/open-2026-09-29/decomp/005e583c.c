
longlong FUN_005e583c(void)

{
  int *piVar1;
  uint in_r3;
  
  piVar1 = DAT_005e5dd8;
  FUN_005eceb2();
  FUN_005e4c84(0);
  if ((((piVar1[0x73] != 0) && (piVar1[0x74] != 0)) && (piVar1[0x75] != 0)) && (piVar1[0x77] != 0))
  {
    FUN_0043dfa4(piVar1[0x73],1);
    FUN_005ea30c();
    FUN_005e482a(piVar1[0x74],DAT_005e625c,6,100);
    FUN_0049942e(piVar1[0x75],DAT_005e6260);
    FUN_0049942e(piVar1[0x77],PTR_s__Tap___hold_to_stop_response__005e6538);
    FUN_005e4902();
  }
  if (*piVar1 != 0) {
    FUN_0043dfa4(*piVar1,1);
  }
  return (ulonglong)in_r3 << 0x20;
}

