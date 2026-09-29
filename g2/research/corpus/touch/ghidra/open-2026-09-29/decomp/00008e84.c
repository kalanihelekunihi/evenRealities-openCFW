
void Cy_GPIO_SetDrivemode(int param_1,uint param_2,uint param_3)

{
  if (7 < param_2) {
    software_bkpt(1);
  }
  if (0xf < param_3) {
    software_bkpt(1);
  }
  *(uint *)(param_1 + 8) =
       (param_3 & 7) << (param_2 * 3 & 0xff) | *(uint *)(param_1 + 8) & ~(7 << (param_2 * 3 & 0xff))
  ;
  *(uint *)(param_1 + 0x18) =
       (param_3 >> 3 & 1) << (param_2 & 0xff) | *(uint *)(param_1 + 0x18) & ~(1 << (param_2 & 0xff))
  ;
  return;
}

