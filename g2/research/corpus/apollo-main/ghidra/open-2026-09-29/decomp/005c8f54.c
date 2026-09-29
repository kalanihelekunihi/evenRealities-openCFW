
void FUN_005c8f54(int param_1)

{
  int local_68;
  undefined4 local_64;
  undefined4 local_58;
  undefined4 local_48;
  undefined4 local_38;
  
  if (*(int *)(param_1 + 0x44) == 0) {
    FUN_005c877a();
  }
  else {
    FUN_004503d6(&local_68);
    local_64 = DAT_005c8fe0;
    local_38 = *(undefined4 *)(param_1 + 0x44);
    local_68 = param_1;
    FUN_004506ce(&local_68,0,1);
    local_48 = DAT_005c8fd0;
    local_58 = DAT_005c8fe4;
    FUN_00450408(&local_68);
  }
  return;
}

