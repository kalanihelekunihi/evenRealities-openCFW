
undefined8 FUN_00550b14(int param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  byte *pbVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_00550ff4;
  pbVar1 = DAT_00550d38;
  if (*(int *)(DAT_00550ff4 + 0x3c) != 0) {
    if ((*DAT_00550d38 == 0) || (*DAT_00550d38 == 4)) {
      iVar3 = FUN_0044e498(*(undefined4 *)(DAT_00550ff4 + 0x3c));
      if ((*DAT_00550f80 != '\0') && (*DAT_00550f84 != 0)) {
        if ((param_1 == 1) && ((int)*DAT_00550ecc < *DAT_00550f84 + -1)) {
          *pbVar1 = 1;
          FUN_00550694(*(undefined4 *)(iVar2 + 0x3c),iVar3 + 0xd6,*DAT_005514d4);
        }
        else if ((param_1 == -1) && (0 < *DAT_00550ecc)) {
          *DAT_00550f7c = *DAT_00550f7c + -1;
          *pbVar1 = 1;
          FUN_00550694(*(undefined4 *)(iVar2 + 0x3c),iVar3 + -0xd6,*DAT_005514d4);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_4 = (uint)*pbVar1;
        param_2 = 0x3ce;
        param_3 = DAT_00551310;
        FUN_0043d574(3,DAT_005514b8,DAT_0055148c,DAT_005514e8,0x3ce,DAT_00551310,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00551318,DAT_00551318,*pbVar1,param_2,param_3,param_4);
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

