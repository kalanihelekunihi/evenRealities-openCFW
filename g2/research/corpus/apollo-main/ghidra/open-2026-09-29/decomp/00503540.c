
void FUN_00503540(void)

{
  int iVar1;
  char cVar2;
  int iVar3;
  
  iVar1 = DAT_005040bc;
  *(undefined1 *)(DAT_005040bc + 0x96) = 0;
  iVar3 = iVar1;
  for (cVar2 = '\n'; cVar2 != '\0'; cVar2 = cVar2 + -1) {
    *(undefined1 *)(iVar3 + 6) = 0xff;
    iVar3 = iVar3 + 0xf;
  }
  *(undefined1 *)(iVar1 + 0x9c) = 0;
  return;
}

