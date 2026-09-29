
void hciEvtParseReadLocalSupCodecCapCmdCmpl(int param_1,undefined1 *param_2)

{
  byte bVar1;
  byte *pbVar2;
  byte bVar3;
  byte bVar4;
  
  *(undefined1 *)(param_1 + 4) = *param_2;
  bVar3 = param_2[1];
  pbVar2 = param_2 + 2;
  if (4 < bVar3) {
    bVar3 = 5;
  }
  *(byte *)(param_1 + 5) = bVar3;
  for (bVar3 = 0; bVar3 < *(byte *)(param_1 + 5); bVar3 = bVar3 + 1) {
    bVar1 = *pbVar2;
    bVar4 = bVar1;
    if (3 < bVar1) {
      bVar4 = 4;
    }
    *(byte *)(param_1 + (uint)bVar3 * 5 + 6) = bVar4;
    FUN_00439be4(param_1 + (uint)bVar3 * 5 + 7,pbVar2 + 1,
                 *(undefined1 *)(param_1 + (uint)bVar3 * 5 + 6));
    pbVar2 = pbVar2 + 1 + bVar1;
  }
  *(undefined1 *)(param_1 + 3) = *(undefined1 *)(param_1 + 4);
  return;
}

