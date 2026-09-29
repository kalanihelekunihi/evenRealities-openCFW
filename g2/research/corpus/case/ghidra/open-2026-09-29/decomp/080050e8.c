
void HAL_PWR_EnterSLEEPMode(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  if (param_1 == 0) {
    uVar2 = *DAT_08005120 & 0xfffffff8;
  }
  else {
    uVar2 = (*DAT_08005120 & 0xfffffff8) + 1;
  }
  *DAT_08005120 = uVar2;
  iVar1 = DAT_08005124;
  *(uint *)(DAT_08005124 + 0x10) = *(uint *)(DAT_08005124 + 0x10) | 4;
  if (param_2 == 1) {
    WaitForInterrupt();
  }
  else {
    WaitForEvent();
    WaitForEvent();
  }
  *(uint *)(iVar1 + 0x10) = *(uint *)(iVar1 + 0x10) & 0xfffffffb;
  return;
}

