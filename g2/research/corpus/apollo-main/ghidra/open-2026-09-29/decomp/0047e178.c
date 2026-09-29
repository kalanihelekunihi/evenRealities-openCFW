
undefined8 FUN_0047e178(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  
  piVar1 = DAT_0047e2b8;
  if (*DAT_0047e2b4 == '\0') {
    iVar3 = -2;
  }
  else {
    if (*DAT_0047e2b8 != 0) {
      if (0x8000 < (uint)(param_2 + *DAT_0047e2bc)) {
        FUN_0047e06a();
        *piVar1 = 0;
      }
    }
    piVar2 = DAT_0047e2c0;
    if (*DAT_0047e2c0 == 0) {
      if (*piVar1 == 0) {
        iVar3 = FUN_0047e0c8();
      }
      else {
        iVar3 = FUN_0047e144();
      }
      if (iVar3 != 0) goto LAB_0047e1ea;
    }
    iVar3 = file_write(param_1,1,param_2,*piVar2);
    if (iVar3 == param_2) {
      *DAT_0047e2bc = param_2 + *DAT_0047e2bc;
      iVar3 = 0;
    }
    else {
      FUN_0047e06a();
      iVar3 = -5;
    }
  }
LAB_0047e1ea:
  return CONCAT44(param_4,iVar3);
}

