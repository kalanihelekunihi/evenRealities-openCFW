
void hciCoreConnFree(short param_1)

{
  char cVar1;
  int *piVar2;
  
  cVar1 = '\x03';
  piVar2 = DAT_0052ae14;
  while( true ) {
    if (cVar1 == '\0') {
      return;
    }
    if ((short)piVar2[4] == param_1) break;
    cVar1 = cVar1 + -1;
    piVar2 = piVar2 + 7;
  }
  if (*piVar2 != 0) {
    WsfMsgFree(*piVar2);
    *piVar2 = 0;
  }
  *(undefined1 *)((int)piVar2 + 0x16) = 0;
  if (piVar2[2] != 0) {
    WsfMsgFree(piVar2[2]);
    piVar2[2] = 0;
  }
  *(undefined2 *)(piVar2 + 4) = 0xffff;
  hciCoreTxReady(*(undefined1 *)((int)piVar2 + 0x19));
  return;
}

