
void Cy_GPIO_Write(int param_1,uint param_2,uint param_3)

{
  if (7 < param_2) {
    software_bkpt(1);
  }
  if (param_3 < 2) {
    if (param_3 == 0) {
      *(int *)(param_1 + 0x44) = 1 << (param_2 & 0xff);
      return;
    }
  }
  else {
    software_bkpt(1);
  }
  *(int *)(param_1 + 0x40) = 1 << (param_2 & 0xff);
  return;
}

