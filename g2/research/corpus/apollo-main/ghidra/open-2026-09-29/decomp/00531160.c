
undefined4 attcSetupReq(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar1 = param_2[1];
  uVar2 = param_2[2];
  *(undefined4 *)(param_1 + 4) = *param_2;
  *(undefined4 *)(param_1 + 8) = uVar1;
  *(undefined4 *)(param_1 + 0xc) = uVar2;
  if (*(char *)((int)param_2 + 2) == '\v') {
    FUN_00439be4(param_1 + 0x10,*(undefined4 *)param_2[1],8);
  }
  else {
    FUN_00439be4(param_1 + 0x10,param_2[1],8);
  }
  attcSendReq(param_1);
  return param_4;
}

