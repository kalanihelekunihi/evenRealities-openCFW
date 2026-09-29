
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 af_indic_metrics_init(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = *(undefined4 *)(param_2 + 0x5c);
  *(uint *)(param_1 + 0x28) = (uint)*(ushort *)(param_2 + 0x44);
  iVar1 = FT_Select_Charmap(param_2,_DAT_005a96f0);
  if (iVar1 == 0) {
    af_cjk_metrics_init_widths(param_1,param_2);
    af_cjk_metrics_check_digits(param_1,param_2);
  }
  else {
    *(undefined4 *)(param_2 + 0x5c) = 0;
  }
  FT_Set_Charmap(param_2,uVar2);
  return 0;
}

