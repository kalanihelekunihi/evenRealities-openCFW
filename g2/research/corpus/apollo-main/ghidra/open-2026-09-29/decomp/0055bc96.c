
undefined8 DmL2cConnUpdateInd(undefined1 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined2 uStack_18;
  undefined1 local_16;
  undefined1 uStack_15;
  undefined4 local_14;
  undefined4 local_10;
  
  uStack_18 = (undefined2)param_2;
  local_16 = (undefined1)(param_2 >> 0x10);
  uStack_15 = (undefined1)(param_2 >> 0x18);
  local_14 = param_3;
  local_10 = param_4;
  iVar1 = dmConnCcbByHandle(param_2 & 0xffff);
  if (iVar1 != 0) {
    local_16 = 0x72;
    local_10 = CONCAT31(local_10._1_3_,param_1);
    local_14 = param_3;
    dmConnUpdExecute(iVar1,&uStack_18);
  }
  return CONCAT44(local_14,CONCAT13(uStack_15,CONCAT12(local_16,uStack_18)));
}

