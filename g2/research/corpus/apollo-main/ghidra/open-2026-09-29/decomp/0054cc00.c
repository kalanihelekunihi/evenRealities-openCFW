
int FUN_0054cc00(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  piVar1 = DAT_0054cfb8;
  if (*(int *)s_8l7_pAp_0054cf88._0_4_ < 5) {
    iVar2 = 0;
  }
  else {
    iVar4 = (*(int *)s_8l7_pAp_0054cf88._0_4_ + -5) * 0x28;
    if (iVar4 < 0) {
      iVar4 = 0;
    }
    iVar2 = *DAT_0054cfb8 * 0x28;
    if (iVar4 < *DAT_0054cfb8 * 0x28) {
      iVar2 = iVar4;
    }
    if (iVar2 < 0) {
      iVar2 = 0;
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,DAT_0054cfc0,0xc75,DAT_0054cfbc,
                   param_1,*piVar1,iVar2,iVar4,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x11000000,DAT_0054d92c,DAT_0054d92c,param_1,*piVar1,iVar2,iVar4);
    }
  }
  return iVar2;
}

