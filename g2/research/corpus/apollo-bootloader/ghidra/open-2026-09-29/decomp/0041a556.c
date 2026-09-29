
void FUN_0041a556(int param_1)

{
  int iVar1;
  char cVar2;
  
  FUN_0041b3e4();
  cVar2 = *(char *)(param_1 + 0x45);
  while (('\0' < cVar2 && (*(int *)(param_1 + 0x24) != 0))) {
    iVar1 = FUN_0041872c(param_1 + 0x24);
    if (iVar1 != 0) {
      FUN_004189a2();
    }
    cVar2 = cVar2 + -1;
  }
  *(undefined1 *)(param_1 + 0x45) = 0xff;
  FUN_0041b3fc();
  FUN_0041b3e4();
  cVar2 = *(char *)(param_1 + 0x44);
  while (('\0' < cVar2 && (*(int *)(param_1 + 0x10) != 0))) {
    iVar1 = FUN_0041872c(param_1 + 0x10);
    if (iVar1 != 0) {
      FUN_004189a2();
    }
    cVar2 = cVar2 + -1;
  }
  *(undefined1 *)(param_1 + 0x44) = 0xff;
  FUN_0041b3fc();
  return;
}

