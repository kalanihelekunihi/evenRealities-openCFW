
void Cy_GPIO_SetInterruptEdge(int param_1,uint param_2,uint param_3)

{
  if (8 < param_2) {
    software_bkpt(1);
  }
  if (3 < param_3) {
    software_bkpt(1);
  }
  *(uint *)(param_1 + 0xc) =
       (param_3 & 3) << (param_2 << 1 & 0xff) |
       *(uint *)(param_1 + 0xc) & ~(3 << (param_2 << 1 & 0xff));
  return;
}

