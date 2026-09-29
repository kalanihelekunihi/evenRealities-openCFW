
void hciEvtParseReadLocalSupCodecsCmdCmpl(int param_1,byte *param_2)

{
  byte bVar1;
  byte *pbVar2;
  byte bVar3;
  
  *(byte *)(param_1 + 4) = *param_2;
  bVar1 = param_2[1];
  bVar3 = bVar1;
  if (4 < bVar1) {
    bVar3 = 5;
  }
  *(byte *)(param_1 + 5) = bVar3;
  for (bVar3 = 0; pbVar2 = param_2 + 2, bVar3 < *(byte *)(param_1 + 5); bVar3 = bVar3 + 1) {
    *(byte *)((uint)bVar3 + param_1 + 6) = *pbVar2;
    *(byte *)((uint)bVar3 + param_1 + 0xb) = param_2[3];
    param_2 = pbVar2;
  }
  if (5 < bVar1) {
    pbVar2 = pbVar2 + (uint)bVar1 * 2 + -10;
  }
  bVar1 = *pbVar2;
  pbVar2 = pbVar2 + 1;
  if (4 < bVar1) {
    bVar1 = 5;
  }
  *(byte *)(param_1 + 0x10) = bVar1;
  for (bVar1 = 0; bVar1 < *(byte *)(param_1 + 0x10); bVar1 = bVar1 + 1) {
    *(ushort *)(param_1 + (uint)bVar1 * 4 + 0x12) = (ushort)pbVar2[1] * 0x100 + (ushort)*pbVar2;
    *(ushort *)(param_1 + (uint)bVar1 * 4 + 0x14) = (ushort)pbVar2[3] * 0x100 + (ushort)pbVar2[2];
    *(byte *)((uint)bVar1 + param_1 + 0x26) = pbVar2[4];
    pbVar2 = pbVar2 + 5;
  }
  *(undefined1 *)(param_1 + 3) = *(undefined1 *)(param_1 + 4);
  return;
}

