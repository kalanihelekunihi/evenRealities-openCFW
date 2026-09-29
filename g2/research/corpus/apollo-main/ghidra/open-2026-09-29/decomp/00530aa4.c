
uint l2cHciFlowCback(undefined2 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  ushort uVar3;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  uVar3 = DmConnIdByHandle(param_1);
  uVar2 = uStack_10;
  iVar1 = DAT_00530b90;
  uStack_10 = (uint)uVar3;
  if (uVar3 != 0) {
    uStack_10._3_1_ = SUB41(uVar2,3);
    uStack_10._0_3_ = CONCAT12(param_2,uVar3);
    (**(code **)(DAT_00530b90 + 0xc))(&uStack_10);
    uStack_10._0_3_ = CONCAT12(param_2,(undefined2)uStack_10);
    (**(code **)(iVar1 + 0x10))(&uStack_10);
    uStack_10._0_3_ = CONCAT12(param_2,(undefined2)uStack_10);
    (**(code **)(iVar1 + 0x14))(&uStack_10);
  }
  return uStack_10;
}

