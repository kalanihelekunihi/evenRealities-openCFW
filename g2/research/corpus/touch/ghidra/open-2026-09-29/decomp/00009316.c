
void Cy_SCB_SetRxFifoLevel(uint *param_1,uint param_2)

{
  uint uVar1;
  
  if ((*param_1 & 0xc000) == 0) {
    uVar1 = 0x10;
  }
  else {
    uVar1 = 8;
  }
  if (uVar1 <= param_2) {
    software_bkpt(1);
  }
  param_1[0xc1] = param_1[0xc1] & 0xffffff00 | param_2 & 0xff;
  return;
}

