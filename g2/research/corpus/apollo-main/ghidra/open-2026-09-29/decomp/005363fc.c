
char FUN_005363fc(void)

{
  int iVar1;
  char cVar2;
  
  iVar1 = DAT_00536498;
  cVar2 = *(char *)(DAT_00536498 + 0x38);
  *(char *)(DAT_00536498 + 0x38) = *(char *)(DAT_00536498 + 0x38) + '\x01';
  if (cVar2 == -1) {
    cVar2 = *(char *)(iVar1 + 0x38);
    *(char *)(iVar1 + 0x38) = *(char *)(iVar1 + 0x38) + '\x01';
  }
  return cVar2;
}

