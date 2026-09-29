
char FUN_0047a676(char param_1)

{
  char cVar1;
  int iVar2;
  byte bVar3;
  
  cVar1 = '\0';
  iVar2 = DAT_0047ae64;
  for (bVar3 = 0; bVar3 < 10; bVar3 = bVar3 + 1) {
    if ((*(char *)(iVar2 + 0x2f) != '\0') && (*(char *)(iVar2 + 0xc3) == param_1)) {
      cVar1 = cVar1 + '\x01';
    }
    iVar2 = iVar2 + 200;
  }
  return cVar1;
}

