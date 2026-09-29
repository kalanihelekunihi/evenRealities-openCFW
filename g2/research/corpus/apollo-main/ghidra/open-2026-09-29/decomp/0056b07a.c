
void hciEvtParseLeBigInfoAdvRpt(undefined2 *param_1,byte *param_2)

{
  param_1[2] = (ushort)param_2[1] * 0x100 + (ushort)*param_2;
  *(byte *)(param_1 + 3) = param_2[2];
  *(byte *)((int)param_1 + 7) = param_2[3];
  param_1[4] = (ushort)param_2[5] * 0x100 + (ushort)param_2[4];
  *(byte *)(param_1 + 5) = param_2[6];
  *(byte *)((int)param_1 + 0xb) = param_2[7];
  *(byte *)(param_1 + 6) = param_2[8];
  param_1[7] = (ushort)param_2[10] * 0x100 + (ushort)param_2[9];
  *(uint *)(param_1 + 8) =
       (uint)param_2[0xc] * 0x100 + (uint)param_2[0xb] + (uint)param_2[0xd] * 0x10000;
  param_1[10] = (ushort)param_2[0xf] * 0x100 + (ushort)param_2[0xe];
  *(byte *)(param_1 + 0xb) = param_2[0x10];
  *(byte *)((int)param_1 + 0x17) = param_2[0x11];
  *(byte *)(param_1 + 0xc) = param_2[0x12];
  *(undefined1 *)((int)param_1 + 3) = 0;
  *param_1 = param_1[2];
  return;
}

