
void hciCoreConnAlloc(undefined2 param_1)

{
  char cVar1;
  int iVar2;
  
  cVar1 = '\x03';
  iVar2 = DAT_0052ae14;
  while( true ) {
    if (cVar1 == '\0') {
      return;
    }
    if (*(short *)(iVar2 + 0x10) == -1) break;
    cVar1 = cVar1 + -1;
    iVar2 = iVar2 + 0x1c;
  }
  *(undefined2 *)(iVar2 + 0x10) = param_1;
  *(undefined1 *)(iVar2 + 0x17) = 0;
  *(undefined1 *)(iVar2 + 0x19) = 0;
  *(undefined1 *)(iVar2 + 0x18) = 0;
  return;
}

