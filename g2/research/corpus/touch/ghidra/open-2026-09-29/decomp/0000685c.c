
void touch_sub_355c(int *param_1)

{
  uint *puVar1;
  
  puVar1 = (uint *)**(undefined4 **)(*param_1 + 8);
  *puVar1 = *puVar1 & 0x7fffffff;
  puVar1[0x20] = 0;
  if (-1 < *(int *)(**(int **)(*param_1 + 8) + 0x180) << 0x1f) {
    puVar1[0x51] = 1;
    touch_sub_3308(0x13b,0,param_1);
  }
  *puVar1 = *puVar1 | 0x80000000;
  puVar1[0x1d] = 0;
  puVar1[0x4a] = 0;
  puVar1[0x48] = DAT_000068e0;
  puVar1[0x40] = DAT_000068e4;
  *(undefined1 *)(param_1[2] + 0x71) = 0;
  *puVar1 = *puVar1 & DAT_000068e8;
  puVar1[2] = puVar1[2] | 0x10000000;
  return;
}

