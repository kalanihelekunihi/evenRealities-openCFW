
undefined8 cff_get_ps_name(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int *piVar2;
  int iVar3;
  
  iVar3 = *(int *)(param_1 + 0x2a4);
  if (((int)((uint)*(byte *)(param_1 + 8) << 0x1c) < 0) && (*(int *)(param_1 + 0x21c) != 0)) {
    uVar1 = FT_Get_Module(*(undefined4 *)(*(int *)(param_1 + 0x60) + 4),DAT_005ace00);
    piVar2 = (int *)ft_module_get_service(uVar1,PTR_s_postscript_font_name_005ad080,0);
    if ((piVar2 != (int *)0x0) && (*piVar2 != 0)) {
      uVar1 = (*(code *)*piVar2)(param_1);
      goto LAB_005ac412;
    }
  }
  uVar1 = *(undefined4 *)(iVar3 + 0x544);
LAB_005ac412:
  return CONCAT44(param_4,uVar1);
}

