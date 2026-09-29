
void FUN_00454574(int param_1)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  
  piVar4 = *(int **)(param_1 + 0x2ac);
  while (piVar4[0x11] != 0) {
    FUN_00484622();
    FUN_00484548();
  }
  iVar2 = FUN_0044fc52(param_1);
  if (iVar2 != 0) {
    FUN_00454692(*(undefined4 *)(DAT_00454634 + 0x10));
  }
  *(undefined4 *)(param_1 + 0x30) = 1;
  if (*(int *)(param_1 + 0x38) << 0x1f < 0) {
    bVar1 = (byte)((uint)(*(int *)(param_1 + 0x38) << 0x1e) >> 0x1f);
  }
  else {
    bVar1 = 0;
  }
  if (bVar1 == 0) {
    *(undefined4 *)(param_1 + 0x34) = 0;
  }
  else {
    *(undefined4 *)(param_1 + 0x34) = 1;
  }
  iVar2 = *(int *)(param_1 + 0x34);
  if (*(int *)(param_1 + 0x28) != 0) {
    FUN_00454648(param_1,param_1 + 0x30c,*(undefined4 *)(*piVar4 + 0x10));
  }
  iVar3 = FUN_0044fc52(param_1);
  if ((iVar3 != 0) && ((*(char *)(param_1 + 0x39) != '\x01' || (iVar2 != 0)))) {
    if (*(int *)(param_1 + 0x24) == *(int *)(param_1 + 0x1c)) {
      *(undefined4 *)(param_1 + 0x24) = *(undefined4 *)(param_1 + 0x20);
    }
    else {
      *(undefined4 *)(param_1 + 0x24) = *(undefined4 *)(param_1 + 0x1c);
    }
  }
  return;
}

