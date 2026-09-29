
void aout_dac_config(int param_1,int *param_2)

{
  *(uint *)(param_1 + 0x18) = *param_2 << 0x1f | *(uint *)(param_1 + 0x18) & 0x3fffffff;
  *(uint *)(param_1 + 0x18) = (uint)*(byte *)(param_2 + 1) << 0x10 | *(uint *)(param_1 + 0x18);
  *(uint *)(param_1 + 0x18) = (uint)*(ushort *)((int)param_2 + 6);
  *(uint *)(param_1 + 0x18) =
       (*(ushort *)(param_2 + 2) & 3) << 0x18 | *(uint *)(param_1 + 0x18) & 0xfcffffff;
  *(uint *)(param_1 + 0x1c) = param_2[3] << 0x1f | *(uint *)(param_1 + 0x1c) & 0x3fffffff;
  *(uint *)(param_1 + 0x1c) = (uint)*(byte *)(param_2 + 4) << 0x10 | *(uint *)(param_1 + 0x1c);
  *(uint *)(param_1 + 0x1c) = (uint)*(ushort *)((int)param_2 + 0x12);
  *(uint *)(param_1 + 0x1c) =
       (*(ushort *)(param_2 + 5) & 3) << 0x18 | *(uint *)(param_1 + 0x1c) & 0xfcffffff;
  *(uint *)(param_1 + 0x2c) = param_2[6] << 0x1f | *(uint *)(param_1 + 0x2c) & 0x3fffffff;
  *(uint *)(param_1 + 0x2c) = (param_2[7] & 7U) << 0x17 | *(uint *)(param_1 + 0x2c);
  *(uint *)(param_1 + 0x2c) = (param_2[8] & 7U) << 0x10 | *(uint *)(param_1 + 0x2c);
  return;
}

