
void FUN_10012398(undefined4 param_1,undefined4 param_2)

{
  uint uVar1;
  undefined4 local_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  uint uStack_c;
  int iStack_8;
  
  local_20 = param_1;
  uStack_1c = param_2;
  FUN_10012694(&local_20,&uStack_18);
  uVar1 = iStack_8 << 2 | uStack_c >> 0x1e;
  if ((uStack_c & 0x1fffffff) != 0) {
    uVar1 = uVar1 | 1;
  }
  FUN_100124ec(uStack_18,uStack_14,uStack_10,uVar1);
  return;
}

