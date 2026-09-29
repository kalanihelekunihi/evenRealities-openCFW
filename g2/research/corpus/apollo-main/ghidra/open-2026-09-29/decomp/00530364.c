
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

short WsfBufInit(ushort param_1,int param_2,byte param_3,ushort *param_4)

{
  ushort uVar1;
  int *piVar2;
  short *psVar3;
  ushort *puVar4;
  ushort *puVar5;
  byte bVar6;
  
  piVar2 = DAT_00530514;
  *DAT_00530514 = param_2;
  puVar5 = (ushort *)*piVar2;
  puVar4 = puVar5 + (uint)param_3 * 6;
  *DAT_00530518 = param_3;
  while( true ) {
    psVar3 = _DAT_0053051c;
    if ((ushort *)(*piVar2 + (uint)(param_1 >> 3) * 8) < puVar4) {
      return 0;
    }
    if (param_3 == 0) {
      *_DAT_0053051c = (short)puVar4 - (short)*piVar2;
      return *psVar3;
    }
    if (*param_4 < 8) {
      *puVar5 = 8;
    }
    else if ((*param_4 & 7) == 0) {
      *puVar5 = *param_4;
    }
    else {
      *puVar5 = (*param_4 + 8) - ((byte)*param_4 & 7);
    }
    *(byte *)(puVar5 + 1) = (byte)param_4[1];
    param_4 = param_4 + 2;
    *(ushort **)(puVar5 + 2) = puVar4;
    *(ushort **)(puVar5 + 4) = puVar4;
    uVar1 = *puVar5 >> 3;
    for (bVar6 = (byte)puVar5[1]; 1 < bVar6; bVar6 = bVar6 - 1) {
      if ((ushort *)(*piVar2 + (uint)(param_1 >> 3) * 8) < puVar4) {
        return 0;
      }
      *(ushort **)puVar4 = puVar4 + (uint)uVar1 * 4;
      puVar4 = puVar4 + (uint)uVar1 * 4;
    }
    if ((ushort *)(*piVar2 + (uint)(param_1 >> 3) * 8) < puVar4) break;
    puVar4[0] = 0;
    puVar4[1] = 0;
    puVar4 = puVar4 + (uint)uVar1 * 4;
    puVar5 = puVar5 + 6;
    param_3 = param_3 - 1;
  }
  return 0;
}

