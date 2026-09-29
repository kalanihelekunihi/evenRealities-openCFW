
void FUN_005d4510(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_3c;
  undefined4 uStack_38;
  undefined4 local_34;
  undefined4 uStack_30;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  local_1c = 1;
  local_3c = *(undefined4 *)(param_1 + 0x2dd0);
  uStack_38 = *(undefined4 *)(param_1 + 0x2dd4);
  uStack_18 = param_4;
  iVar1 = FUN_005d36ea(param_1 + 8);
  if (iVar1 == 0) {
    FUN_005d4754(param_1,*(undefined4 *)(param_1 + 0x2dd8),*(undefined4 *)(param_1 + 0x2ddc));
  }
  FUN_005d4040(param_1,param_1 + 8,&local_34,param_2,param_3);
  (*(code *)**(undefined4 **)(param_1 + 4))(*(undefined4 *)(param_1 + 4),&local_3c);
  *(undefined4 *)(param_1 + 0x2dd0) = local_34;
  *(undefined4 *)(param_1 + 0x2dd4) = uStack_30;
  *(undefined4 *)(param_1 + 0x2db8) = param_2;
  *(undefined4 *)(param_1 + 0x2dbc) = param_3;
  return;
}

