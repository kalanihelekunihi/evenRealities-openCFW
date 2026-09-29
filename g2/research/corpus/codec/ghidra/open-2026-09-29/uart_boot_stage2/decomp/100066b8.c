
uint FUN_100066b8(uint param_1,byte *param_2,uint param_3)

{
  byte bVar1;
  uint *puVar2;
  uint uVar3;
  byte *pbVar4;
  byte *pbVar5;
  
  param_1 = ~param_1;
  if (((uint)param_2 & 3) != 0) {
    if (param_3 == 0) goto LAB_100066f0;
    do {
      bVar1 = *param_2;
      param_3 = param_3 - 1;
      param_2 = param_2 + 1;
      param_1 = param_1 >> 8 ^ *(uint *)(PTR_DAT_10006770 + ((bVar1 ^ param_1) & 0xff) * 4);
      if (param_3 == 0) goto LAB_100066f0;
    } while (((uint)param_2 & 3) != 0);
  }
  puVar2 = (uint *)(param_2 + -4);
  if (param_3 >> 2 != 0) {
    do {
      puVar2 = puVar2 + 1;
      uVar3 = *(uint *)(PTR_DAT_10006770 + ((param_1 ^ *puVar2) & 0xff) * 4) ^
              (param_1 ^ *puVar2) >> 8;
      uVar3 = *(uint *)(PTR_DAT_10006770 + (uVar3 & 0xff) * 4) ^ uVar3 >> 8;
      uVar3 = *(uint *)(PTR_DAT_10006770 + (uVar3 & 0xff) * 4) ^ uVar3 >> 8;
      param_1 = *(uint *)(PTR_DAT_10006770 + (uVar3 & 0xff) * 4) ^ uVar3 >> 8;
    } while (puVar2 != (uint *)(param_2 + ((param_3 >> 2) + 0x3fffffff) * 4));
  }
  if ((param_3 & 3) != 0) {
    pbVar4 = (byte *)((int)puVar2 + 3);
    pbVar5 = pbVar4 + (param_3 & 3);
    do {
      pbVar4 = pbVar4 + 1;
      param_1 = param_1 >> 8 ^ *(uint *)(PTR_DAT_10006770 + ((*pbVar4 ^ param_1) & 0xff) * 4);
    } while (pbVar4 != pbVar5);
    return ~param_1;
  }
LAB_100066f0:
  return ~param_1;
}

