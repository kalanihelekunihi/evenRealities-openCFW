
undefined8 FUN_00508f34(int param_1,undefined4 param_2,uint param_3,int param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  undefined4 local_20;
  int iStack_1c;
  
  local_20 = param_3;
  iStack_1c = param_4;
  uVar1 = FUN_00508ed2(param_2,param_3);
  if (uVar1 == 0) {
    local_20._0_2_ = CONCAT11((char)param_2,(char)((uint)param_2 >> 8));
    (**(code **)(param_1 + 0xc))(4);
    uVar1 = FUN_00508eb6(param_1,0x7c,2,&local_20);
    if (uVar1 == 0) {
      for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1) {
        (**(code **)(param_1 + 0xc))(4);
        uVar2 = FUN_00508e9a(param_1,0x7e,1,param_4 + uVar3);
        uVar1 = uVar1 | uVar2;
      }
    }
  }
  return CONCAT44(local_20,uVar1);
}

