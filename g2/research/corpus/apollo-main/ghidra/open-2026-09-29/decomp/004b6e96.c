
undefined1 DmConnIdByHandle(short param_1)

{
  int iVar1;
  char cVar2;
  
  cVar2 = '\x03';
  iVar1 = DAT_004b7430;
  while( true ) {
    if (cVar2 == '\0') {
      return 0;
    }
    if ((*(char *)(iVar1 + 0x16) != '\0') && (*(short *)(iVar1 + 0xc) == param_1)) break;
    cVar2 = cVar2 + -1;
    iVar1 = iVar1 + 0x30;
  }
  return *(undefined1 *)(iVar1 + 0x10);
}

