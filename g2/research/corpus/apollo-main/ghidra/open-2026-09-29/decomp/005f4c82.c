
void SetSuperRound(int param_1,short param_2,uint param_3)

{
  uint uVar1;
  
  uVar1 = param_3 & 0xc0;
  if (uVar1 == 0) {
    *(int *)(param_1 + 0x1e0) = (int)param_2 / 2;
  }
  else if (uVar1 == 0x40) {
    *(int *)(param_1 + 0x1e0) = (int)param_2;
  }
  else if (uVar1 == 0x80) {
    *(int *)(param_1 + 0x1e0) = (int)param_2 << 1;
  }
  else if (uVar1 == 0xc0) {
    *(int *)(param_1 + 0x1e0) = (int)param_2;
  }
  uVar1 = param_3 & 0x30;
  if (uVar1 == 0) {
    *(undefined4 *)(param_1 + 0x1e4) = 0;
  }
  else if (uVar1 == 0x10) {
    *(int *)(param_1 + 0x1e4) = *(int *)(param_1 + 0x1e0) / 4;
  }
  else if (uVar1 == 0x20) {
    *(int *)(param_1 + 0x1e4) = *(int *)(param_1 + 0x1e0) / 2;
  }
  else if (uVar1 == 0x30) {
    *(int *)(param_1 + 0x1e4) = (*(int *)(param_1 + 0x1e0) * 3) / 4;
  }
  if ((param_3 & 0xf) == 0) {
    *(int *)(param_1 + 0x1e8) = *(int *)(param_1 + 0x1e0) + -1;
  }
  else {
    *(int *)(param_1 + 0x1e8) = (int)(*(int *)(param_1 + 0x1e0) * ((param_3 & 0xf) - 4)) / 8;
  }
  *(int *)(param_1 + 0x1e0) = *(int *)(param_1 + 0x1e0) >> 8;
  *(int *)(param_1 + 0x1e4) = *(int *)(param_1 + 0x1e4) >> 8;
  *(int *)(param_1 + 0x1e8) = *(int *)(param_1 + 0x1e8) >> 8;
  return;
}

