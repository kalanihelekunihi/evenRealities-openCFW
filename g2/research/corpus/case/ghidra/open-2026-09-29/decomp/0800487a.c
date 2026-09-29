
undefined4 FUN_0800487a(undefined4 *param_1)

{
  uint *puVar1;
  
  if (param_1 != (undefined4 *)0x0) {
    if (*(char *)((int)param_1 + 0x25) == '\x02') {
      *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffff1;
      *(uint *)param_1[0x12] = *(uint *)param_1[0x12] & 0xfffffeff;
      *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffffe;
      *(int *)(param_1[0x10] + 4) = 1 << (param_1[0x11] & 0x1c);
      *(undefined4 *)(param_1[0x13] + 4) = param_1[0x14];
      puVar1 = (uint *)param_1[0x15];
      if (puVar1 != (uint *)0x0) {
        *puVar1 = *puVar1 & 0xfffffeff;
        *(undefined4 *)(param_1[0x16] + 4) = param_1[0x17];
      }
      *(undefined1 *)((int)param_1 + 0x25) = 1;
      *(undefined1 *)(param_1 + 9) = 0;
      return 0;
    }
    param_1[0xf] = 4;
    *(undefined1 *)(param_1 + 9) = 0;
  }
  return 1;
}

