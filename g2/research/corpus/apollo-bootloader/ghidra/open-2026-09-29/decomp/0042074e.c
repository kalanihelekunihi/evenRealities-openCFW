
int FUN_0042074e(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  memset_wrapper_426c10(&local_10,0,5,param_4,param_1,param_2);
  iVar1 = FUN_004205f4(5,0,0,&local_10,1);
  if (iVar1 == 0) {
    if (local_10 << 0x1f < 0) {
      iVar1 = 1;
    }
    else {
      iVar1 = 0;
    }
  }
  else {
    elog_output(2,DAT_00420adc,DAT_00420978,DAT_00421000,0x376,DAT_00420ffc);
  }
  return iVar1;
}

