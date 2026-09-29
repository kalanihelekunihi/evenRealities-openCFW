
void FUN_00441f88(int param_1)

{
  int iVar1;
  char cVar2;
  
  FUN_004420d0();
  cVar2 = *(char *)(param_1 + 0x45);
  while (('\0' < cVar2 && (*(int *)(param_1 + 0x24) != 0))) {
    iVar1 = FUN_00455370(param_1 + 0x24);
    if (iVar1 != 0) {
      vTaskMissedYield();
    }
    cVar2 = cVar2 + -1;
  }
  *(undefined1 *)(param_1 + 0x45) = 0xff;
  FUN_004420e8();
  FUN_004420d0();
  cVar2 = *(char *)(param_1 + 0x44);
  while (('\0' < cVar2 && (*(int *)(param_1 + 0x10) != 0))) {
    iVar1 = FUN_00455370(param_1 + 0x10);
    if (iVar1 != 0) {
      vTaskMissedYield();
    }
    cVar2 = cVar2 + -1;
  }
  *(undefined1 *)(param_1 + 0x44) = 0xff;
  FUN_004420e8();
  return;
}

