
char AUDM_activeAppCount(void)

{
  char cVar1;
  int iVar2;
  
  cVar1 = '\0';
  for (iVar2 = 0; iVar2 < 8; iVar2 = iVar2 + 1) {
    if (*(char *)(DAT_0054f978 + iVar2) == '\x01') {
      cVar1 = cVar1 + '\x01';
    }
  }
  return cVar1;
}

