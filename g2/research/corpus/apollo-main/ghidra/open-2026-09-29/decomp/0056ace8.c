
void hciEvtParseLeSetCigParamsCmdCmpl(ushort *param_1,undefined1 *param_2)

{
  byte *pbVar1;
  ushort *puVar2;
  char cVar3;
  
  puVar2 = param_1 + 4;
  *(undefined1 *)(param_1 + 2) = *param_2;
  *(undefined1 *)((int)param_1 + 5) = param_2[1];
  *(undefined1 *)(param_1 + 3) = param_2[2];
  pbVar1 = param_2 + 3;
  if (0x10 < (byte)param_1[3]) {
    *(undefined1 *)(param_1 + 3) = 0x10;
  }
  for (cVar3 = (char)param_1[3]; cVar3 != '\0'; cVar3 = cVar3 + -1) {
    *puVar2 = (ushort)pbVar1[1] * 0x100 + (ushort)*pbVar1;
    pbVar1 = pbVar1 + 2;
    puVar2 = puVar2 + 1;
  }
  *(char *)((int)param_1 + 3) = (char)param_1[2];
  *param_1 = (ushort)*(byte *)((int)param_1 + 5);
  return;
}

