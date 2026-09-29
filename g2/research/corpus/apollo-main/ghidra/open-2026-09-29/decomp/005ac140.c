
undefined4 cff_get_glyph_name(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int *piVar2;
  int iVar3;
  
  iVar3 = *(int *)(param_1 + 0x2a4);
  if (*(char *)(iVar3 + 0x18) == '\x02') {
    uVar1 = FT_Get_Module(*(undefined4 *)(*(int *)(param_1 + 0x60) + 4),DAT_005ace00);
    piVar2 = (int *)ft_module_get_service(uVar1,DAT_005ace04,0);
    if ((piVar2 == (int *)0x0) || (*piVar2 == 0)) {
      uVar1 = 0xb;
    }
    else {
      uVar1 = (*(code *)*piVar2)(param_1,param_2,param_3,param_4);
    }
  }
  else if (*(int *)(iVar3 + 0xc0c) == 0) {
    uVar1 = 0xb;
  }
  else {
    iVar3 = cff_index_get_sid_string(iVar3,*(undefined2 *)(*(int *)(iVar3 + 0x4a4) + param_2 * 2));
    if (iVar3 != 0) {
      ft_mem_strcpyn(param_3,iVar3,param_4);
    }
    uVar1 = 0;
  }
  return uVar1;
}

