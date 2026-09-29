
void HAL_PWR_DisableWakeUpPin(uint param_1)

{
  *(uint *)(DAT_080050a4 + 8) = *(uint *)(DAT_080050a4 + 8) & ~(param_1 & 0x3f);
  return;
}

