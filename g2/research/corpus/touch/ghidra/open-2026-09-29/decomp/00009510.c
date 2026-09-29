
void SlaveHandleAck(int param_1,char *param_2)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  
  uVar2 = *(uint *)(param_1 + 100) & 0x10;
  if (*(code **)(param_2 + 0x44) != (code *)0x0) {
    if (uVar2 == 0) {
      uVar1 = 2;
    }
    else {
      uVar1 = 1;
    }
    (**(code **)(param_2 + 0x44))(uVar1);
  }
  if (uVar2 == 0) {
    *(undefined4 *)(param_2 + 4) = DAT_000095b0;
    *(uint *)(param_2 + 0x20) = *(uint *)(param_2 + 0x20) | 0x10;
    *(undefined4 *)(param_1 + DAT_000095b4) = 1;
    iVar3 = 0;
    if ((*param_2 != '\0') && (iVar3 = 0, *(int *)(param_2 + 0x3c) != 0)) {
      *(uint *)(param_1 + 0x60) = *(uint *)(param_1 + 0x60) | 0x2000;
      uVar2 = *(uint *)(param_2 + 0x3c);
      if (uVar2 < 0x11) {
        iVar3 = uVar2 - 1;
        *(uint *)(param_1 + 0x60) = *(uint *)(param_1 + 0x60) | 0x8000;
        *(undefined4 *)(param_1 + DAT_000095b4) = 0;
      }
      else if (uVar2 - 0x10 < 0x11) {
        iVar3 = uVar2 - 0x11;
      }
      else {
        iVar3 = 7;
      }
    }
    Cy_SCB_SetRxFifoLevel(param_1,iVar3);
  }
  else {
    *(undefined4 *)(param_2 + 4) = DAT_000095a8;
    *(uint *)(param_2 + 0x20) = *(uint *)(param_2 + 0x20) | 1;
    *(undefined4 *)(param_2 + 0x30) = *(undefined4 *)(param_2 + 0x34);
    param_2[0x24] = '\0';
    *(undefined4 *)(param_1 + DAT_000095ac) = 1;
  }
  return;
}

