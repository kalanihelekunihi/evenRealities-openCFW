
void SlaveHandleStop(uint *param_1,int param_2,char *param_3)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = *(uint *)(param_3 + 0x20);
  if (*(int *)(param_3 + 4) == DAT_000094f4) {
    if ((param_1[0xc2] & 0x1ff) != 0) {
      if ((*param_3 == '\0') && ((uVar3 & 0x200) != 0)) {
        *(uint *)(param_3 + 0x20) = *(uint *)(param_3 + 0x20) | 0x40;
        Cy_SCB_SetRxFifoLevel(param_1,0);
      }
      else if (*param_3 == '\0') {
        if ((param_2 == 0) && (-1 < *(int *)((int)param_1 + DAT_000094fc) << 0x19)) {
          *(uint *)(param_3 + 0x20) = *(uint *)(param_3 + 0x20) | 0x40;
        }
      }
      else {
        *(uint *)(param_3 + 0x20) = *(uint *)(param_3 + 0x20) | 0x40;
        param_1[0xc1] = param_1[0xc1] | 0x10000;
        param_1[0xc1] = param_1[0xc1] & DAT_00009504;
      }
    }
    *(uint *)(param_3 + 0x20) = *(uint *)(param_3 + 0x20) | 0x20;
    *(uint *)(param_3 + 0x20) = *(uint *)(param_3 + 0x20) & 0xffffffef;
    param_1[0x18] = param_1[0x18] & DAT_00009508;
    iVar2 = DAT_0000950c;
    *(undefined4 *)((int)param_1 + DAT_0000950c) = 0;
    *(undefined4 *)((int)param_1 + iVar2 + -8) = 1;
    uVar1 = 0x20;
  }
  else {
    iVar2 = (param_1[0x82] >> 0xf & 1) + (param_1[0x82] & 0x1ff);
    *(int *)(param_3 + 0x34) = *(int *)(param_3 + 0x30) - iVar2;
    if (-1 < *(int *)(param_3 + 0x20) << 0x1c) {
      *(int *)(param_3 + 0x2c) = *(int *)(param_3 + 0x2c) + iVar2;
      *(int *)(param_3 + 0x28) = *(int *)(param_3 + 0x28) - iVar2;
    }
    *(uint *)(param_3 + 0x20) = *(uint *)(param_3 + 0x20) | 4;
    *(uint *)(param_3 + 0x20) = *(uint *)(param_3 + 0x20) & 0xfffffffe;
    *(undefined4 *)((int)param_1 + DAT_000094f8) = 0;
    uVar1 = 0x10;
  }
  if ((*(uint *)((int)param_1 + DAT_000094fc) & 0x101) != 0) {
    *param_1 = *param_1 & 0x7fffffff;
    param_1[0x1a] = 0;
    param_1[0x1b] = 0;
    *param_1 = *param_1 | 0x80000000;
    uVar1 = uVar1 | 0x40;
  }
  param_3[4] = '\0';
  param_3[5] = '\0';
  param_3[6] = '\0';
  param_3[7] = '\x10';
  if ((uVar3 & 0x200) != 0) {
    *(uint *)(param_3 + 0x20) = *(uint *)(param_3 + 0x20) & DAT_00009500;
  }
  if (*(code **)(param_3 + 0x44) != (code *)0x0) {
    (**(code **)(param_3 + 0x44))(uVar1);
  }
  return;
}

