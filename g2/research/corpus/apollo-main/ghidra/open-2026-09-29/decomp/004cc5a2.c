
undefined8 FUN_004cc5a2(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint local_18;
  int local_14;
  
  local_18 = param_3;
  local_14 = param_4;
  iVar1 = FUN_004cbefc(param_1,param_3,param_1 + 0x48);
  if (iVar1 == 0) {
    FUN_004cae54(param_3 + 0x18);
    local_18 = DAT_004ccf78 | (*(byte *)(param_3 + 0x17) + 0x600) * 0x100000;
    local_14 = param_3 + 0x18;
    iVar1 = FUN_004cd388(param_1,param_2,&local_18,1);
    FUN_004cae3e(param_3 + 0x18);
    if (iVar1 == 0) {
      iVar1 = 0;
    }
  }
  return CONCAT44(local_18,iVar1);
}

