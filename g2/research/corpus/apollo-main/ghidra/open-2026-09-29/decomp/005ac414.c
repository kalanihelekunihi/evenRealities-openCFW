
undefined4 cff_get_cmap_info(int *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int *piVar2;
  undefined4 uVar3;
  
  uVar3 = 0;
  if (((undefined *)param_1[3] == PTR_DAT_005ad084) || ((undefined *)param_1[3] == PTR_DAT_005ad088)
     ) {
    uVar3 = 0x96;
  }
  else {
    uVar1 = FT_Get_Module(*(undefined4 *)(*(int *)(*param_1 + 0x60) + 4),DAT_005ace00);
    piVar2 = (int *)ft_module_get_service(uVar1,PTR_s_tt_cmaps_005ad08c,0);
    if ((piVar2 != (int *)0x0) && (*piVar2 != 0)) {
      uVar3 = (*(code *)*piVar2)(param_1,param_2);
    }
  }
  return uVar3;
}

