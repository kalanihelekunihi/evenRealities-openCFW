
undefined4 FUN_100121e0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 local_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  uint auStack_34 [5];
  uint auStack_20 [5];
  
  local_44 = param_1;
  uStack_40 = param_2;
  uStack_3c = param_3;
  uStack_38 = param_4;
  FUN_10012694(&local_44,auStack_34);
  FUN_10012694(&uStack_3c,auStack_20);
  if ((1 < auStack_34[0]) && (1 < auStack_20[0])) {
    uVar1 = FUN_10012778(auStack_34,auStack_20);
    return uVar1;
  }
  return 0xffffffff;
}

