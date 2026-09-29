
undefined8 FUN_00505fcc(undefined4 param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  undefined4 local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  uVar1 = FUN_0050668e(param_1);
  uVar2 = FUN_00508e5c(param_1,0x10,1,&local_18);
  local_18 = CONCAT31(local_18._1_3_,(byte)local_18 & 0xfc | param_2 & 3);
  uVar3 = FUN_00508e74(param_1,0x10,1,&local_18);
  return CONCAT44(local_18,uVar1 | uVar2 | uVar3);
}

