
undefined8
SmpScCalcF4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
           undefined1 param_5,undefined4 param_6)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 *puVar3;
  undefined4 local_28;
  
  iVar1 = SmpScAlloc(0x41,param_1,param_2);
  local_28 = param_3;
  if (iVar1 != 0) {
    uVar2 = SmpScCat(iVar1,param_3,0x20);
    puVar3 = (undefined1 *)SmpScCat(uVar2,param_4,0x20);
    *puVar3 = param_5;
    SmpScCmac(param_6,iVar1,0x41,param_1);
    local_28 = param_2;
  }
  return CONCAT44(param_4,local_28);
}

