
void Cy_SysTick_Init(undefined4 param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  
  if (0xffffff < param_2) {
    software_bkpt(1);
  }
  for (uVar2 = 0; uVar2 < 5; uVar2 = uVar2 + 1) {
    *(undefined4 *)(uVar2 * 4 + DAT_0000a698) = 0;
  }
  *(undefined4 *)(DAT_0000a69c + 0x3c) = DAT_0000a6a0;
  Cy_SysTick_SetClockSource();
  iVar1 = DAT_0000a6a4;
  if (0xffffff < param_2) {
    software_bkpt(1);
  }
  *(uint *)(DAT_0000a6a4 + 4) = param_2 & 0xffffff;
  *(undefined4 *)(iVar1 + 8) = 0;
  Cy_SysTick_Enable();
  return;
}

