
undefined8 FUN_005b05d0(undefined4 param_1,undefined4 param_2,int param_3,int *param_4)

{
  int iVar1;
  int local_10;
  int *piStack_c;
  
  if (param_3 == 0x44) {
    iVar1 = 0x45;
  }
  else {
    iVar1 = param_3;
    if (param_3 == 0x45) {
      iVar1 = 0x44;
    }
  }
  local_10 = param_3;
  piStack_c = param_4;
  if (param_3 != 10) {
    if (param_3 == 0x42) {
      iVar1 = FUN_005b16d0(iVar1);
      if (iVar1 != 6) {
        iVar1 = 0;
        if (param_4 != (int *)0x0) {
          iVar1 = *param_4;
        }
        if ((((iVar1 != 0) && (iVar1 != 0x21)) && (*(int *)(DAT_005b0a74 + 0x20) != 0)) &&
           (*DAT_005b0a74 == '\x02')) {
          FUN_00441488(*(undefined4 *)(DAT_005b0a74 + 0x20),0x7f,0);
        }
      }
      goto LAB_005b06a8;
    }
    if (param_3 == 0x43) {
      iVar1 = FUN_005b16d0(iVar1);
      if (((iVar1 != 6) && (*(int *)(DAT_005b0a74 + 0x20) != 0)) && (*DAT_005b0a74 == '\x02')) {
        FUN_00441488(*(undefined4 *)(DAT_005b0a74 + 0x20),0xff,0);
      }
      goto LAB_005b06a8;
    }
    if (((param_3 != 0x44) && (param_3 != 0x45)) && (param_3 != 0x48)) {
      if (param_3 == 0x4f) {
        iVar1 = FUN_0045a568();
        if (iVar1 == 1) {
          local_10 = *(int *)PTR_DAT_005b0a78;
          piStack_c = *(int **)(PTR_DAT_005b0a78 + 4);
          FUN_0048eb32(DAT_005b0a4c,2,&local_10);
        }
        FUN_005b02e4(0x13,0);
      }
      goto LAB_005b06a8;
    }
  }
  FUN_005b15e0(iVar1,param_4);
LAB_005b06a8:
  return CONCAT44(local_10,1);
}

