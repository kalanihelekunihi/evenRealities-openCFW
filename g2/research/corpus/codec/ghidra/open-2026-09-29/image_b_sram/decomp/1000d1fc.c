
void FUN_1000d1fc(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  iVar4 = *(int *)(param_1 + 0x18);
  iVar5 = *(int *)(param_1 + 8);
  iVar7 = *(int *)(param_1 + 0x10);
  iVar3 = *(int *)(param_1 + 4);
  iVar2 = *(int *)(param_1 + 0xc);
  iVar8 = *(int *)(param_1 + 0x14);
  iVar6 = *(int *)(param_1 + 0x1c);
  FUN_10009934(PTR_s_frequency_bins___d_1000d2a0,iVar4);
  iVar1 = iVar5 * iVar4 * 4;
  iVar8 = iVar8 * 2 + param_2;
  iVar3 = iVar3 * iVar5;
  *(int *)(param_1 + 0x78) = iVar8;
  iVar8 = iVar8 + iVar1;
  *(int *)(param_1 + 0x84) = param_2;
  *(int *)(param_1 + 0x7c) = iVar8;
  iVar8 = iVar8 + iVar1;
  *(int *)(param_1 + 0x6c) = iVar8;
  iVar8 = iVar8 + iVar3 * 8;
  *(int *)(param_1 + 0xcc) = iVar8;
  iVar8 = iVar8 + (iVar3 - iVar5) * 8;
  iVar3 = iVar5 * 8;
  *(int *)(param_1 + 200) = iVar8;
  iVar8 = iVar8 + iVar3;
  *(int *)(param_1 + 0xd0) = iVar8;
  iVar8 = iVar8 + iVar3;
  *(int *)(param_1 + 0x68) = iVar8;
  iVar8 = iVar8 + iVar3;
  *(int *)(param_1 + 0x90) = iVar8;
  iVar8 = iVar8 + iVar1;
  *(int *)(param_1 + 0x88) = iVar8;
  iVar8 = iVar8 + (iVar2 + (iVar5 + -1) * iVar7) * 2;
  *(int *)(param_1 + 0x80) = iVar8;
  iVar8 = iVar8 + iVar6 * (iVar2 - iVar7) * 2;
  *(int *)(param_1 + 0xa0) = iVar8;
  iVar8 = iVar8 + iVar4 * 4;
  *(int *)(param_1 + 0x98) = iVar8;
  *(int *)(param_1 + 0x9c) = iVar8 + iVar4 * 4;
  return;
}

