
undefined8
DmL2cConnUpdateCnf(undefined2 param_1,undefined2 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined2 uStack_10;
  undefined1 local_e;
  undefined1 uStack_d;
  undefined2 local_c;
  undefined2 uStack_a;
  
  local_c = (undefined2)param_4;
  uStack_a = (undefined2)((uint)param_4 >> 0x10);
  uStack_10 = (undefined2)param_3;
  local_e = (undefined1)((uint)param_3 >> 0x10);
  uStack_d = (undefined1)((uint)param_3 >> 0x18);
  iVar1 = dmConnCcbByHandle(param_1);
  if (iVar1 != 0) {
    local_e = 0x73;
    local_c = param_2;
    dmConnUpdExecute(iVar1,&uStack_10);
  }
  return CONCAT26(uStack_a,CONCAT24(local_c,CONCAT13(uStack_d,CONCAT12(local_e,uStack_10))));
}

