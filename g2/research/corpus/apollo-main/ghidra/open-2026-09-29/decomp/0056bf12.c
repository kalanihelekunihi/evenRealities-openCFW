
undefined8 AttcDiscService(undefined1 param_1,undefined4 param_2,byte param_3,undefined4 param_4)

{
  uint uVar1;
  
  uVar1 = (uint)param_3;
  AttcFindByTypeValueReq(param_1,1,0xffff,0x2800,uVar1,param_4,0);
  return CONCAT44(param_4,uVar1);
}

