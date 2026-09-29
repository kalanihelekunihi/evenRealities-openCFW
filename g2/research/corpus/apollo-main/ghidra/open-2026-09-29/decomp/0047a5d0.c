
undefined4 FUN_0047a5d0(int param_1)

{
  int iVar1;
  char cVar2;
  
  cVar2 = '\n';
  iVar1 = DAT_0047ae64;
  while( true ) {
    if (cVar2 == '\0') {
      return 0;
    }
    if (((*(char *)(iVar1 + 0x2f) != '\0') && (*(char *)(iVar1 + 0x30) != '\0')) &&
       (iVar1 == param_1)) break;
    cVar2 = cVar2 + -1;
    iVar1 = iVar1 + 200;
  }
  return 1;
}

