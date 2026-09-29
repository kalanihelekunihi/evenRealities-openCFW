
undefined1 FUN_004bb05a(void)

{
  int iVar1;
  char cVar2;
  
  cVar2 = '\x03';
  iVar1 = DAT_004bb3ac;
  while( true ) {
    if (cVar2 == '\0') {
      return 0;
    }
    if (*(char *)(iVar1 + 4) != '\0') break;
    cVar2 = cVar2 + -1;
    iVar1 = iVar1 + 0x30;
  }
  return *(undefined1 *)(iVar1 + 4);
}

