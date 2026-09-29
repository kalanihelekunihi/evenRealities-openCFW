
undefined8 FUN_00505e2e(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  uint uVar1;
  undefined4 uVar2;
  uint local_18;
  undefined4 uStack_14;
  
  uVar2 = 0;
  local_18 = param_3;
  uStack_14 = param_4;
  FUN_0043c0e4(&local_18,1,0);
  uVar1 = *(uint *)(param_1 + 8);
  if (uVar1 != 0) {
    if (uVar1 == 2) {
      local_18 = local_18 & 0xfffffffb | 8;
      uVar2 = FUN_00508e74(param_1,0x2d,1,&local_18);
    }
    else if (uVar1 < 2) {
      local_18 = local_18 | 0xc;
      uVar2 = FUN_00508e74(param_1,0x2d,1,&local_18);
    }
    else {
      uVar2 = 0xfffffff5;
    }
  }
  return CONCAT44(local_18,uVar2);
}

