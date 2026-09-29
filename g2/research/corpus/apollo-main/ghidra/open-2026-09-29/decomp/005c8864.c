
void FUN_005c8864(int param_1)

{
  int local_70;
  undefined4 local_6c;
  undefined4 local_50;
  int local_40;
  int local_34;
  undefined4 local_2c;
  
  local_40 = FUN_005c790a(param_1,0x60000);
  if (local_40 == 0) {
    FUN_00450500(param_1,DAT_005c8fcc);
    *(byte *)(param_1 + 100) = *(byte *)(param_1 + 100) | 1;
  }
  else {
    FUN_004503d6(&local_70);
    local_6c = DAT_005c8fcc;
    local_70 = param_1;
    local_34 = local_40;
    FUN_004506ce(&local_70,1,0);
    local_50 = DAT_005c8fd0;
    local_2c = 0xffffffff;
    FUN_00450408(&local_70);
  }
  return;
}

