
void hciEvtParseLeCisEst(undefined2 *param_1,undefined1 *param_2)

{
  *(undefined1 *)(param_1 + 2) = *param_2;
  param_1[3] = (ushort)(byte)param_2[2] * 0x100 + (ushort)(byte)param_2[1];
  *(uint *)(param_1 + 4) =
       (uint)(byte)param_2[4] * 0x100 + (uint)(byte)param_2[3] + (uint)(byte)param_2[5] * 0x10000;
  *(uint *)(param_1 + 6) =
       (uint)(byte)param_2[7] * 0x100 + (uint)(byte)param_2[6] + (uint)(byte)param_2[8] * 0x10000;
  *(uint *)(param_1 + 8) =
       (uint)(byte)param_2[10] * 0x100 + (uint)(byte)param_2[9] + (uint)(byte)param_2[0xb] * 0x10000
  ;
  *(uint *)(param_1 + 10) =
       (uint)(byte)param_2[0xd] * 0x100 + (uint)(byte)param_2[0xc] +
       (uint)(byte)param_2[0xe] * 0x10000;
  *(undefined1 *)(param_1 + 0xc) = param_2[0xf];
  *(undefined1 *)((int)param_1 + 0x19) = param_2[0x10];
  *(undefined1 *)(param_1 + 0xd) = param_2[0x11];
  *(undefined1 *)((int)param_1 + 0x1b) = param_2[0x12];
  *(undefined1 *)(param_1 + 0xe) = param_2[0x13];
  *(undefined1 *)((int)param_1 + 0x1d) = param_2[0x14];
  *(undefined1 *)(param_1 + 0xf) = param_2[0x15];
  param_1[0x10] = (ushort)(byte)param_2[0x17] * 0x100 + (ushort)(byte)param_2[0x16];
  param_1[0x11] = (ushort)(byte)param_2[0x19] * 0x100 + (ushort)(byte)param_2[0x18];
  param_1[0x12] = (ushort)(byte)param_2[0x1b] * 0x100 + (ushort)(byte)param_2[0x1a];
  *(undefined1 *)((int)param_1 + 3) = *(undefined1 *)(param_1 + 2);
  *param_1 = param_1[3];
  return;
}

