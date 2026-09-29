
void gx8002_dma_descriptors(int *param_1,int *param_2,int param_3,int param_4,byte param_5)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  ushort auStack_34 [4];
  
  auStack_34[0] = 0xfff;
  auStack_34[1] = 0xf001;
  auStack_34[2] = 0;
  auStack_34[3] = 0;
  iVar5 = (uint)param_5 * (uint)auStack_34[(param_1[3] & 0x3ffU) >> 9];
  iVar4 = (uint)param_5 * (uint)auStack_34[(param_1[3] & 0xffU) >> 7];
  iVar6 = 0;
  iVar1 = 0;
  iVar2 = 0;
  while( true ) {
    if (param_3 + -1 <= iVar6) break;
    *param_2 = *param_1 + iVar1;
    param_2[1] = iVar2 + param_1[1];
    iVar3 = param_1[3];
    param_2[4] = 0xfff;
    param_2[3] = iVar3;
    iVar3 = virt_to_dma(param_2 + 6);
    param_2[2] = iVar3;
    iVar6 = iVar6 + 1;
    iVar1 = iVar5 + iVar1;
    iVar2 = iVar4 + iVar2;
    param_2 = param_2 + 6;
  }
  *param_2 = *param_1 + iVar6 * iVar5;
  param_2[1] = param_1[1] + iVar6 * iVar4;
  param_2[3] = param_1[3] & 0xe7ffffff;
  param_4 = param_4 % 0xfff;
  if (param_4 == 0) {
    param_4 = 0xfff;
  }
  param_2[4] = param_4;
  param_2[2] = 0;
  return;
}

