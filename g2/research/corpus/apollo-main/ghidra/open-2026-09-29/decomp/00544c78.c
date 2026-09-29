
void FUN_00544c78(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_3c;
  uint local_38;
  int local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined1 auStack_28 [24];
  undefined4 uStack_10;
  
  local_38 = 0;
  local_3c = 0;
  uStack_10 = param_4;
  FUN_00544736(param_1,auStack_28,1,&local_38,&local_3c,DAT_00545540,0);
  if (local_38 < 2) {
    local_2c = local_3c;
    local_34 = param_1;
    local_30 = param_2;
    FUN_00544736(param_1,auStack_28,0,&local_34,0,DAT_00545544,0);
  }
  *(undefined1 *)(param_1 + 0x30) = 0;
  return;
}

