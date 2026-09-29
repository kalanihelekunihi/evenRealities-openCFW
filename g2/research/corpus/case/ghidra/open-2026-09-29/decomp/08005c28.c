
undefined4 case_enable_peripheral_context(int *param_1)

{
  uint *puVar1;
  
  if (*(char *)((int)param_1 + 0x3d) != '\x01') {
    return 1;
  }
  *(undefined1 *)((int)param_1 + 0x3d) = 2;
  *(uint *)(*param_1 + 0xc) = *(uint *)(*param_1 + 0xc) | 1;
  puVar1 = (uint *)*param_1;
  if ((((puVar1 == DAT_08005c78) || (puVar1 == DAT_08005c7c)) || (puVar1 == DAT_08005c80)) ||
     (puVar1 == DAT_08005c84)) {
    if ((puVar1[2] & DAT_08005c88) == 6) {
      return 0;
    }
    if ((puVar1[2] & DAT_08005c88) == DAT_08005c88 - 7) {
      return 0;
    }
  }
  *puVar1 = *puVar1 | 1;
  return 0;
}

