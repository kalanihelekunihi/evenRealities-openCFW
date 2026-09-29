
void hciEvtParseLeCreateBigCmpl(ushort *param_1,undefined1 *param_2)

{
  byte *pbVar1;
  byte bVar2;
  
  *(undefined1 *)(param_1 + 2) = *param_2;
  *(undefined1 *)((int)param_1 + 5) = param_2[1];
  *(uint *)(param_1 + 4) =
       (uint)(byte)param_2[3] * 0x100 + (uint)(byte)param_2[2] + (uint)(byte)param_2[4] * 0x10000;
  *(uint *)(param_1 + 6) =
       (uint)(byte)param_2[6] * 0x100 + (uint)(byte)param_2[5] + (uint)(byte)param_2[7] * 0x10000;
  *(undefined1 *)(param_1 + 8) = param_2[8];
  *(undefined1 *)((int)param_1 + 0x11) = param_2[9];
  *(undefined1 *)(param_1 + 9) = param_2[10];
  *(undefined1 *)((int)param_1 + 0x13) = param_2[0xb];
  *(undefined1 *)(param_1 + 10) = param_2[0xc];
  param_1[0xb] = (ushort)(byte)param_2[0xe] * 0x100 + (ushort)(byte)param_2[0xd];
  param_1[0xc] = (ushort)(byte)param_2[0x10] * 0x100 + (ushort)(byte)param_2[0xf];
  bVar2 = param_2[0x11];
  pbVar1 = param_2 + 0x12;
  if (0xf < bVar2) {
    bVar2 = 0x10;
  }
  *(byte *)(param_1 + 0xd) = bVar2;
  for (bVar2 = 0; bVar2 < (byte)param_1[0xd]; bVar2 = bVar2 + 1) {
    param_1[bVar2 + 0xe] = (ushort)pbVar1[1] * 0x100 + (ushort)*pbVar1;
    pbVar1 = pbVar1 + 2;
  }
  *(char *)((int)param_1 + 3) = (char)param_1[2];
  *param_1 = (ushort)*(byte *)((int)param_1 + 5);
  return;
}

