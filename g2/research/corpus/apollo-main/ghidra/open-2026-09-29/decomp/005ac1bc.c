
uint cff_get_name_index(int param_1,undefined4 param_2)

{
  ushort uVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  iVar6 = *(int *)(param_1 + 0x2a4);
  if (*(char *)(iVar6 + 0x18) == '\x02') {
    uVar2 = FT_Get_Module(*(undefined4 *)(*(int *)(param_1 + 0x60) + 4),DAT_005ace00);
    iVar6 = ft_module_get_service(uVar2,DAT_005ace04,0);
    if ((iVar6 == 0) || (*(int *)(iVar6 + 4) == 0)) {
      uVar3 = 0;
    }
    else {
      uVar3 = (**(code **)(iVar6 + 4))(param_1,param_2);
    }
  }
  else {
    iVar4 = ft_module_get_service(*(undefined4 *)(param_1 + 0x60),DAT_005ace08,1);
    if (iVar4 == 0) {
      uVar3 = 0;
    }
    else {
      for (uVar3 = 0; uVar3 < *(uint *)(iVar6 + 0x14); uVar3 = uVar3 + 1) {
        uVar1 = *(ushort *)(*(int *)(iVar6 + 0x4a4) + uVar3 * 2);
        if (uVar1 < 0x187) {
          iVar5 = (**(code **)(iVar4 + 0x14))(uVar1);
        }
        else {
          iVar5 = cff_index_get_string(iVar6,uVar1 - 0x187);
        }
        if ((iVar5 != 0) && (iVar5 = FUN_0046cacc(param_2,iVar5), iVar5 == 0)) {
          return uVar3;
        }
      }
      uVar3 = 0;
    }
  }
  return uVar3;
}

