
undefined8 FUN_00508fa6(int param_1,undefined4 param_2,uint param_3,undefined1 *param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  undefined4 local_20;
  undefined1 *puStack_1c;
  
  local_20 = param_3;
  puStack_1c = param_4;
  uVar1 = FUN_00508ed2(param_2,param_3);
  uVar3 = local_20;
  if (uVar1 == 0) {
    local_20._3_1_ = SUB41(uVar3,3);
    local_20._0_3_ = CONCAT12(*param_4,CONCAT11((char)param_2,(char)((uint)param_2 >> 8)));
    (**(code **)(param_1 + 0xc))(4);
    uVar1 = FUN_00508eb6(param_1,0x7c,3,&local_20);
    (**(code **)(param_1 + 0xc))(4);
    if (uVar1 == 0) {
      for (uVar3 = 1; uVar3 < param_3; uVar3 = uVar3 + 1) {
        uVar2 = FUN_00508eb6(param_1,0x7e,1,param_4 + uVar3);
        uVar1 = uVar1 | uVar2;
        (**(code **)(param_1 + 0xc))(4);
      }
    }
  }
  return CONCAT44(local_20,uVar1);
}

