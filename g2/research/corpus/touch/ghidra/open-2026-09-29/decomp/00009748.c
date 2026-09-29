
void SlaveHandleDataReceive(int param_1,char *param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = *(uint *)(param_2 + 0x20);
  if (*(int *)(param_2 + 0x3c) == 0) {
    *(uint *)(param_1 + 0x6c) = *(uint *)(param_1 + 0x6c) | 2;
    *(undefined4 *)(param_1 + DAT_000097f8) = 0;
  }
  else if ((uVar3 & 0x200) == 0 && *param_2 == '\0') {
    *(uint *)(param_1 + 0x6c) = *(uint *)(param_1 + 0x6c) | 1;
    *(char *)(*(int *)(param_2 + 0x38) + *(int *)(param_2 + 0x40)) =
         (char)*(undefined4 *)(param_1 + 0x340);
    *(int *)(param_2 + 0x40) = *(int *)(param_2 + 0x40) + 1;
    *(int *)(param_2 + 0x3c) = *(int *)(param_2 + 0x3c) + -1;
  }
  else {
    iVar1 = Cy_SCB_ReadArray(param_1,*(undefined4 *)(param_2 + 0x38),
                             (*(uint *)(param_1 + 0x304) & 0xff) + 1);
    *(int *)(param_2 + 0x40) = *(int *)(param_2 + 0x40) + iVar1;
    uVar2 = *(int *)(param_2 + 0x3c) - iVar1;
    *(uint *)(param_2 + 0x3c) = uVar2;
    *(int *)(param_2 + 0x38) = *(int *)(param_2 + 0x38) + iVar1;
    if (uVar2 < 0x11) {
      if ((uVar3 & 0x200) == 0) {
        *(uint *)(param_1 + 0x60) = *(uint *)(param_1 + 0x60) | 0x8000;
      }
      iVar1 = *(int *)(param_2 + 0x3c);
      if (iVar1 != 0) {
        iVar1 = iVar1 + -1;
      }
      *(undefined4 *)(param_1 + DAT_000097f8) = 0;
    }
    else if (uVar2 - 0x10 < 0x11) {
      iVar1 = uVar2 - 0x11;
    }
    else {
      iVar1 = 7;
    }
    Cy_SCB_SetRxFifoLevel(param_1,iVar1);
  }
  return;
}

