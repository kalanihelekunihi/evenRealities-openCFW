
void SlaveHandleAddress(uint *param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  if (*(int *)(param_2 + 0x20) << 0x16 < 0) {
    param_1[0x81] = param_1[0x81] | 0x10000;
    param_1[0x81] = param_1[0x81] & DAT_00009724;
    uVar3 = param_1[0x19];
    if (*(code **)(param_2 + 0x44) != (code *)0x0) {
      if ((uVar3 & 0x10) == 0) {
        uVar1 = 2;
      }
      else {
        uVar1 = 1;
      }
      (**(code **)(param_2 + 0x44))(uVar1);
    }
    if ((uVar3 & 0x10) != 0) {
      *(undefined4 *)(param_2 + 4) = DAT_00009728;
      *(uint *)(param_2 + 0x20) = *(uint *)(param_2 + 0x20) | 1;
      *(undefined4 *)(param_2 + 0x30) = *(undefined4 *)(param_2 + 0x34);
      *(undefined1 *)(param_2 + 0x24) = 0;
      *(undefined4 *)((int)param_1 + DAT_0000972c) = 1;
      return;
    }
    *(undefined4 *)(param_2 + 4) = DAT_00009730;
    *(uint *)(param_2 + 0x20) = *(uint *)(param_2 + 0x20) | 0x10;
    if (*(int *)(param_2 + 0x3c) == 0) {
      param_1[0x1b] = param_1[0x1b] | 2;
      iVar2 = 0;
    }
    else {
      *(undefined4 *)((int)param_1 + DAT_00009734) = 1;
      uVar3 = *(uint *)(param_2 + 0x3c);
      if (uVar3 < 0x11) {
        iVar2 = uVar3 - 1;
        *(undefined4 *)((int)param_1 + DAT_00009734) = 0;
      }
      else if (uVar3 - 0x10 < 0x11) {
        iVar2 = uVar3 - 0x11;
      }
      else {
        iVar2 = 7;
      }
    }
    Cy_SCB_SetRxFifoLevel(param_1,iVar2);
    return;
  }
  if (*(code **)(param_2 + 0x48) == (code *)0x0) {
    iVar2 = 0;
  }
  else {
    uVar3 = *param_1 & 0x10000;
    if (((*param_1 & 0x10000) != 0) &&
       (uVar3 = *(uint *)((int)param_1 + DAT_00009738) & 0x40,
       (*(uint *)((int)param_1 + DAT_00009738) & 0x40) != 0)) {
      uVar3 = 2;
    }
    if (((int)(param_1[0x18] << 0x14) < 0) || (-1 < *(int *)((int)param_1 + DAT_00009738) << 0x18))
    {
      if (uVar3 == 0) {
        iVar2 = 0;
        goto LAB_000096e2;
      }
    }
    else {
      uVar3 = uVar3 | 1;
    }
    iVar2 = (**(code **)(param_2 + 0x48))(uVar3);
    param_1[0x3f0] = 1;
    if (iVar2 == 0) {
      param_1[0x3d0] = 0x10;
      uVar1 = DAT_00009740;
      if (*(char *)(param_2 + 2) == '\0') {
        uVar1 = 0x1d1;
      }
      *(undefined4 *)((int)param_1 + DAT_0000973c) = uVar1;
    }
    else if (iVar2 == 1) {
      *(undefined4 *)((int)param_1 + DAT_0000973c) = 0x1c1;
      uVar1 = 0x1c1;
      if (*(char *)(param_2 + 2) != '\0') {
        uVar1 = DAT_00009744;
      }
      *(undefined4 *)((int)param_1 + DAT_0000973c) = uVar1;
    }
  }
LAB_000096e2:
  param_1[0x81] = param_1[0x81] | 0x10000;
  param_1[0x81] = param_1[0x81] & DAT_00009724;
  if (iVar2 != 2) {
    if (iVar2 == 0) {
      uVar3 = 1;
    }
    else {
      uVar3 = 2;
    }
    param_1[0x1b] = param_1[0x1b] | uVar3;
    if (iVar2 == 0) {
      SlaveHandleAck(param_1,param_2);
    }
  }
  return;
}

