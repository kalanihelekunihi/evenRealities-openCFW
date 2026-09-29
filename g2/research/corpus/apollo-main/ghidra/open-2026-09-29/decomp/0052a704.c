
int hciCoreConnByHandle(short param_1)

{
  int iVar1;
  char cVar2;
  
  cVar2 = '\x03';
  iVar1 = DAT_0052ae14;
  while( true ) {
    if (cVar2 == '\0') {
      return 0;
    }
    if (*(short *)(iVar1 + 0x10) == param_1) break;
    cVar2 = cVar2 + -1;
    iVar1 = iVar1 + 0x1c;
  }
  return iVar1;
}

