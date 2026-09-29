
void FUN_0800b374(int param_1)

{
  int iVar1;
  char cVar2;
  
  FUN_0800bffc();
  cVar2 = *(char *)(param_1 + 0x45);
  if ('\0' < cVar2) {
    do {
      if (*(int *)(param_1 + 0x24) == 0) break;
      iVar1 = FUN_0800cba0(param_1 + 0x24);
      if (iVar1 != 0) {
        FUN_0800c16c();
      }
      cVar2 = cVar2 + -1;
    } while ('\0' < cVar2);
  }
  *(undefined1 *)(param_1 + 0x45) = 0xff;
  FUN_0800c014();
  FUN_0800bffc();
  cVar2 = *(char *)(param_1 + 0x44);
  if ('\0' < cVar2) {
    do {
      if (*(int *)(param_1 + 0x10) == 0) break;
      iVar1 = FUN_0800cba0(param_1 + 0x10);
      if (iVar1 != 0) {
        FUN_0800c16c();
      }
      cVar2 = cVar2 + -1;
    } while ('\0' < cVar2);
  }
  *(undefined1 *)(param_1 + 0x44) = 0xff;
  FUN_0800c014();
  return;
}

