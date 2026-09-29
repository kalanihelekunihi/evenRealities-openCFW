
void HAL_PWR_EnableWakeUpPin(uint param_1)

{
  int iVar1;
  
  iVar1 = DAT_080050c0;
  *(uint *)(DAT_080050c0 + 0xc) = *(uint *)(DAT_080050c0 + 0xc) & ~(param_1 & 0x3f) | param_1 >> 8;
  *(uint *)(iVar1 + 8) = *(uint *)(iVar1 + 8) | param_1 & 0x3f;
  return;
}

