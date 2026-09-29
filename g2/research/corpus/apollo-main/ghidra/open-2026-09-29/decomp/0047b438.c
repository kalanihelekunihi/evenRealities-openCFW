
void FUN_0047b438(int param_1,undefined1 param_2)

{
  int iVar1;
  char cVar2;
  
  if (param_1 == 0) {
    iVar1 = DAT_0047bc10;
    for (cVar2 = '\n'; cVar2 != '\0'; cVar2 = cVar2 + -1) {
      *(undefined1 *)(iVar1 + 0x84) = param_2;
      iVar1 = iVar1 + 200;
    }
  }
  else {
    *(undefined1 *)(param_1 + 0x84) = param_2;
  }
  return;
}

