
char dmConnNum(void)

{
  char cVar1;
  int iVar2;
  char cVar3;
  
  cVar1 = '\0';
  iVar2 = DAT_004b6520;
  for (cVar3 = '\x03'; cVar3 != '\0'; cVar3 = cVar3 + -1) {
    if (*(char *)(iVar2 + 0x16) != '\0') {
      cVar1 = cVar1 + '\x01';
    }
    iVar2 = iVar2 + 0x30;
  }
  return cVar1;
}

