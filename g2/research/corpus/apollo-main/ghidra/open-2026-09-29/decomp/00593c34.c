
undefined8 FUN_00593c34(undefined4 *param_1,uint param_2,int *param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int *local_28;
  int local_24;
  undefined4 uStack_20;
  
  iVar3 = DAT_005944b8;
  local_28 = (int *)*DAT_00594310;
  uVar5 = 0;
  local_24 = *DAT_00594318;
  bVar1 = false;
  uStack_20 = param_4;
  if (*DAT_005944b4 == '\0') {
    iVar3 = FUN_005939a8();
    iVar2 = FUN_005939a0();
    if (iVar3 == iVar2) {
      FUN_00593a78(&uStack_20,&local_28,&local_24);
    }
  }
  else {
    if (*DAT_005944a4 == '\0') {
      *param_1 = *(undefined4 *)(DAT_005944b8 + 0x18);
      uVar5 = 1;
      uVar4 = *(int *)(iVar3 + 0x14) - 1;
      if (((*DAT_00594320 <= uVar4) && (uVar4 <= *DAT_0059432c + *DAT_00594320)) && (1 < param_2)) {
        param_1[1] = uVar4;
        uVar5 = 2;
        bVar1 = true;
      }
    }
    if (*DAT_005944a8 != '\0') {
      FUN_00593a78(&uStack_20,&local_28,&local_24);
    }
  }
  if (*DAT_005944a4 != '\0') {
    param_3 = local_28;
  }
  for (; param_3 < (int *)(local_24 + (int)local_28); param_3 = param_3 + 1) {
    if (*param_3 * -0x80000000 < 0) {
      uVar4 = *param_3 - 1;
      if ((((*DAT_00594320 + 4 <= uVar4) && (uVar4 <= *DAT_0059432c + *DAT_00594320)) &&
          ((uVar5 < 0x20 && ((iVar3 = FUN_00593bf8(*param_3 + -5), iVar3 != 0 && (uVar5 < param_2)))
           ))) && ((uVar5 != 2 || ((!bVar1 || (uVar4 != param_1[1])))))) {
        param_1[uVar5] = uVar4;
        uVar5 = uVar5 + 1;
      }
    }
  }
  return CONCAT44(local_28,uVar5);
}

