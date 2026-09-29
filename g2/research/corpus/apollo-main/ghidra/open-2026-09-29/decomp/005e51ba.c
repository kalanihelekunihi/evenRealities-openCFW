
void FUN_005e51ba(char param_1)

{
  int *piVar1;
  
  FUN_005e7f26();
  if (param_1 == '\x04') {
    AUDM_appRelease(6);
    FUN_005e4878(DAT_005e5dd8[0x7e]);
  }
  FUN_005ec268();
  FUN_005ebbc6();
  FUN_005ec770();
  FUN_005ec9c0();
  FUN_005eceb2();
  FUN_005ea30c();
  FUN_005e65f8();
  piVar1 = DAT_005e5dd8;
  *(undefined1 *)(DAT_005e5dd8 + 0xa0) = 0;
  piVar1[0xa1] = 0;
  FUN_005e4c84(0);
  if (*piVar1 != 0) {
    FUN_0043dfa4(*piVar1,1);
  }
  return;
}

