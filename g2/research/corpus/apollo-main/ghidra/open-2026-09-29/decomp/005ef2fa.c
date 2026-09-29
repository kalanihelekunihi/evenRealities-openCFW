
undefined8 tt_get_interface(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  
  iVar1 = ft_service_list_lookup(DAT_005eff30,param_2);
  if (iVar1 == 0) {
    if (param_1 == 0) {
      iVar1 = 0;
    }
    else if (*(int *)(param_1 + 4) == 0) {
      iVar1 = 0;
    }
    else {
      piVar2 = (int *)FT_Get_Module(*(int *)(param_1 + 4),DAT_005eff34);
      if ((piVar2 == (int *)0x0) || (*(int *)(*piVar2 + 0x14) == 0)) {
        iVar1 = 0;
      }
      else {
        iVar1 = (**(code **)(*(int *)(*piVar2 + 0x14) + 0x10))(param_1,param_2);
      }
    }
  }
  return CONCAT44(param_4,iVar1);
}

