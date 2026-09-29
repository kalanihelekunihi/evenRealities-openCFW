
undefined8 cff_size_request(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  undefined4 *puVar6;
  int iVar7;
  int iVar8;
  undefined4 local_28;
  
  local_28 = param_4;
  if ((int)((uint)*(byte *)(*param_1 + 8) << 0x1e) < 0) {
    iVar1 = (**(code **)(*(int *)(*param_1 + 0x21c) + 0x68))(*param_1,param_2,&local_28);
    if (iVar1 == 0) {
      uVar3 = cff_size_select(param_1,local_28);
      goto LAB_005af762;
    }
    param_1[0xb] = -1;
  }
  FT_Request_Metrics(*param_1,param_2);
  iVar1 = cff_size_get_globals_funcs(param_1);
  if (iVar1 != 0) {
    iVar5 = *(int *)(*param_1 + 0x2a4);
    puVar6 = *(undefined4 **)param_1[10];
    iVar7 = *(int *)(iVar5 + 0x5a0);
    local_28 = 0;
    (**(code **)(iVar1 + 4))(*puVar6,param_1[4],param_1[5],0);
    for (iVar4 = *(int *)(iVar5 + 0x7e8); iVar4 != 0; iVar4 = iVar4 + -1) {
      iVar8 = *(int *)(*(int *)(iVar5 + iVar4 * 4 + 0x7e8) + 0x44);
      if (iVar7 == iVar8) {
        iVar2 = param_1[4];
        iVar8 = param_1[5];
      }
      else {
        iVar2 = FT_MulDiv(param_1[4],iVar7,iVar8);
        iVar8 = FT_MulDiv(param_1[5],iVar7,iVar8);
      }
      local_28 = 0;
      (**(code **)(iVar1 + 4))(puVar6[iVar4],iVar2,iVar8,0);
    }
  }
  uVar3 = 0;
LAB_005af762:
  return CONCAT44(local_28,uVar3);
}

