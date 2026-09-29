
undefined8 FUN_00567ec8(undefined4 *param_1,int *param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int local_18;
  
  local_18 = param_4;
  if (param_1 == (undefined4 *)0x0) {
    iVar1 = 0x25;
  }
  else {
    uVar2 = *param_1;
    if (param_2 == (int *)0x0) {
      iVar1 = 6;
    }
    else {
      iVar3 = DAT_00567f78;
      if (((param_1[0x12] != DAT_00567f70) && (iVar3 = DAT_00567f7c, param_1[0x12] != DAT_00567f74))
         && (iVar1 = FT_Lookup_Renderer(uVar2,param_1[0x12],0), iVar3 = 0, iVar1 != 0)) {
        iVar3 = iVar1 + 0x14;
      }
      if (iVar3 == 0) {
        iVar1 = 0x12;
      }
      else {
        iVar1 = FUN_00567e24(uVar2,iVar3,&local_18);
        if (iVar1 == 0) {
          if ((uint)(DAT_00567f84 + param_1[0x10]) < DAT_00567f80) {
            if ((uint)(DAT_00567f84 + param_1[0x11]) < DAT_00567f80) {
              *(undefined4 *)(local_18 + 0xc) = param_1[0x10] << 10;
              *(undefined4 *)(local_18 + 0x10) = param_1[0x11] << 10;
              iVar1 = (**(code **)(iVar3 + 8))(local_18,param_1);
            }
            else {
              iVar1 = 6;
            }
          }
          else {
            iVar1 = 6;
          }
          if (iVar1 == 0) {
            *param_2 = local_18;
          }
          else {
            FUN_00567f88(local_18);
          }
        }
      }
    }
  }
  return CONCAT44(local_18,iVar1);
}

