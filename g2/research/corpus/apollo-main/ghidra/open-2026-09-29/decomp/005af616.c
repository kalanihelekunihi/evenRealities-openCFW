
longlong cff_size_select(int *param_1,int param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  int iVar6;
  int iVar7;
  uint local_28;
  
  param_1[0xb] = param_2;
  FT_Select_Metrics(*param_1);
  iVar1 = cff_size_get_globals_funcs(param_1);
  local_28 = param_4;
  if (iVar1 != 0) {
    iVar4 = *(int *)(*param_1 + 0x2a4);
    puVar5 = *(undefined4 **)param_1[10];
    iVar6 = *(int *)(iVar4 + 0x5a0);
    (**(code **)(iVar1 + 4))(*puVar5,param_1[4],param_1[5],0);
    for (iVar3 = *(int *)(iVar4 + 0x7e8); local_28 = 0, iVar3 != 0; iVar3 = iVar3 + -1) {
      iVar7 = *(int *)(*(int *)(iVar4 + iVar3 * 4 + 0x7e8) + 0x44);
      if (iVar6 == iVar7) {
        iVar2 = param_1[4];
        iVar7 = param_1[5];
      }
      else {
        iVar2 = FT_MulDiv(param_1[4],iVar6,iVar7);
        iVar7 = FT_MulDiv(param_1[5],iVar6,iVar7);
      }
      (**(code **)(iVar1 + 4))(puVar5[iVar3],iVar2,iVar7,0);
    }
  }
  return (ulonglong)local_28 << 0x20;
}

