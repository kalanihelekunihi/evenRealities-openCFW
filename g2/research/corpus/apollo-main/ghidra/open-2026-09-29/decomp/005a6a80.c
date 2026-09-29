
undefined8
af_cjk_hints_compute_segments(int param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte bVar2;
  byte *pbVar3;
  int iVar4;
  byte *pbVar5;
  byte *pbVar6;
  
  iVar4 = param_1 + (uint)param_2 * 0x544;
  pbVar5 = *(byte **)(iVar4 + 0x34);
  pbVar6 = pbVar5 + *(int *)(iVar4 + 0x2c) * 0x2c;
  iVar4 = af_latin_hints_compute_segments(param_1,param_2);
  if (iVar4 == 0) {
    for (; pbVar5 < pbVar6; pbVar5 = pbVar5 + 0x2c) {
      pbVar3 = *(byte **)(pbVar5 + 0x24);
      bVar1 = *pbVar3;
      *pbVar5 = *pbVar5 & 0xfe;
      while (bVar2 = bVar1 & 3, pbVar3 != *(byte **)(pbVar5 + 0x28)) {
        pbVar3 = *(byte **)(pbVar3 + 0x20);
        bVar1 = *pbVar3;
        if (bVar2 == 0 && (bVar1 & 3) == 0) break;
        if (pbVar3 == *(byte **)(pbVar5 + 0x28)) {
          *pbVar5 = *pbVar5 | 1;
        }
      }
    }
    iVar4 = 0;
  }
  return CONCAT44(param_4,iVar4);
}

