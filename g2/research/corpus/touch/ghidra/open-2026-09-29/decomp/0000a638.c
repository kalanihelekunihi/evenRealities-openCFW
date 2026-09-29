
void Cy_SysTick_SetClockSource(uint param_1)

{
  *DAT_0000a64c = *DAT_0000a64c & 0xfffffffb | (param_1 & 1) << 2;
  return;
}

