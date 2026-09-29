
undefined4 FUN_0047a600(void)

{
  int iVar1;
  char cVar2;
  
  cVar2 = '\n';
  iVar1 = DAT_0047ae64;
  while( true ) {
    if (cVar2 == '\0') {
      return 0;
    }
    if ((*(char *)(iVar1 + 0x2f) != '\0') && (*(char *)(iVar1 + 0xc3) == '\0')) break;
    cVar2 = cVar2 + -1;
    iVar1 = iVar1 + 200;
  }
  return 1;
}

