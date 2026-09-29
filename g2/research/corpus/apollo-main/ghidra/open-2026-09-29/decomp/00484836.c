
undefined8 FUN_00484836(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 local_18;
  
  local_18 = param_4;
  if (*param_1 == 0) {
    uVar1 = FUN_00451598(param_1 + 1);
    iVar2 = FUN_004515a4(param_1 + 1);
    iVar3 = FUN_0048aad8(uVar1,(char)param_1[5]);
    iVar4 = FUN_0048affa(uVar1,iVar2,(char)param_1[5],0);
    *param_1 = iVar4;
    if (*param_1 == 0) {
      local_18 = DAT_004849ec;
      FUN_0044d25c(2,DAT_004849bc,0x1d7,DAT_004849f0);
      uVar1 = 0;
    }
    else {
      *(int *)(DAT_004849a8 + 0x144) = iVar3 * iVar2 + *(int *)(DAT_004849a8 + 0x144);
      iVar2 = FUN_00440fc4((char)param_1[5]);
      if (iVar2 != 0) {
        FUN_0048ac40(*param_1,0);
      }
      uVar1 = *(undefined4 *)(*param_1 + 0x10);
    }
  }
  else {
    uVar1 = *(undefined4 *)(*param_1 + 0x10);
  }
  return CONCAT44(local_18,uVar1);
}

