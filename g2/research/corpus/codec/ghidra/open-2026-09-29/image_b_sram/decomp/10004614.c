
int FUN_10004614(int param_1,byte *param_2,int param_3)

{
  byte bVar1;
  uint *puVar2;
  byte *pbVar3;
  
  if (param_3 < 1) {
    param_3 = 0;
  }
  else {
    puVar2 = *(uint **)(param_1 * 0x80 + DAT_1000464c + 4);
    pbVar3 = param_2 + param_3;
    do {
      bVar1 = *param_2;
      do {
      } while ((puVar2[5] & 0x20) == 0);
      param_2 = param_2 + 1;
      *puVar2 = (uint)bVar1;
    } while (param_2 != pbVar3);
  }
  return param_3;
}

