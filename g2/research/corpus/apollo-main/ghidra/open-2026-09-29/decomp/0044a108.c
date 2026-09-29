
int service_time_calendar_to_epoch(int param_1)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = (*(int *)(param_1 + 0xc) + 2000U) % 100;
  if (*(uint *)(param_1 + 0x10) < 3) {
    iVar2 = 0;
  }
  else if ((uVar1 & 3) == 0) {
    iVar2 = 1;
  }
  else {
    iVar2 = 2;
  }
  iVar2 = *(int *)(param_1 + 0x20) +
          *(int *)(param_1 + 0x1c) * 0x3c +
          *(int *)(param_1 + 0x18) * 0xe10 +
          DAT_0044a3fc *
          (*(int *)(param_1 + 0x14) +
           (((*(int *)(param_1 + 0x10) * 0x16f - 0x16aU) / 0xc + uVar1 * 0x16d + (uVar1 + 3) / 4) -
           iVar2) + 0x2acc);
  if (0x31 < *(uint *)(param_1 + 0x24)) {
    iVar2 = iVar2 + 1;
  }
  return iVar2;
}

