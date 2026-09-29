
void FUN_005d431e(int param_1,undefined4 param_2,int *param_3,undefined4 param_4,undefined4 param_5,
                 char param_6)

{
  int iVar1;
  int iVar2;
  char cVar3;
  int *piVar4;
  int local_50;
  int iStack_4c;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  undefined1 auStack_38 [8];
  undefined4 local_30;
  undefined4 uStack_2c;
  undefined4 local_28;
  undefined4 uStack_4;
  
  uStack_4 = param_4;
  FUN_0043c0e4(&local_50,8,0);
  cVar3 = '\0';
  if (*(int *)(param_1 + 0x2de4) == 2) {
    iVar1 = 0x2de8;
    iVar2 = 0x2df0;
  }
  else {
    iVar1 = 0x2df8;
    iVar2 = 0x2e00;
  }
  piVar4 = (int *)(param_1 + iVar2);
  if (((*piVar4 != *param_3) || (piVar4[1] != param_3[1])) &&
     (cVar3 = FUN_005d40c0(param_1,param_1 + iVar1,piVar4,param_3,&uStack_4,&local_50),
     cVar3 != '\0')) {
    *piVar4 = local_50;
    piVar4[1] = iStack_4c;
  }
  local_48 = *(int *)(param_1 + 0x2dd0);
  local_44 = *(int *)(param_1 + 0x2dd4);
  if (*(int *)(param_1 + 0x2de4) == 2) {
    local_28 = 2;
    if (param_6 == '\0') {
      FUN_005d4040(param_1,param_2,&local_40,*(undefined4 *)(param_1 + 0x2df0),
                   *(undefined4 *)(param_1 + 0x2df4));
    }
    else {
      FUN_005d4040(param_1,param_1 + 0xf24,&local_40,*(undefined4 *)(param_1 + 0x2df0),
                   *(undefined4 *)(param_1 + 0x2df4));
    }
    if ((local_48 != local_40) || (local_44 != local_3c)) {
      (**(code **)(*(int *)(param_1 + 4) + 4))(*(undefined4 *)(param_1 + 4),&local_48);
      *(int *)(param_1 + 0x2dd0) = local_40;
      *(int *)(param_1 + 0x2dd4) = local_3c;
    }
  }
  else if (*(int *)(param_1 + 0x2de4) == 4) {
    local_28 = 4;
    FUN_005d4040(param_1,param_2,&local_40,*(undefined4 *)(param_1 + 0x2df0),
                 *(undefined4 *)(param_1 + 0x2df4));
    FUN_005d4040(param_1,param_2,auStack_38,*(undefined4 *)(param_1 + 0x2df8),
                 *(undefined4 *)(param_1 + 0x2dfc));
    FUN_005d4040(param_1,param_2,&local_30,*(undefined4 *)(param_1 + 0x2e00),
                 *(undefined4 *)(param_1 + 0x2e04));
    (**(code **)(*(int *)(param_1 + 4) + 0xc))(*(undefined4 *)(param_1 + 4),&local_48);
    *(undefined4 *)(param_1 + 0x2dd0) = local_30;
    *(undefined4 *)(param_1 + 0x2dd4) = uStack_2c;
  }
  if ((cVar3 == '\0') || (param_6 != '\0')) {
    if (param_6 == '\0') {
      FUN_005d4040(param_1,param_2,&local_40,*param_3,param_3[1]);
    }
    else {
      FUN_005d4040(param_1,param_1 + 0xf24,&local_40,*param_3,param_3[1]);
    }
    if ((local_40 != *(int *)(param_1 + 0x2dd0)) || (local_3c != *(int *)(param_1 + 0x2dd4))) {
      local_28 = 2;
      local_48 = *(int *)(param_1 + 0x2dd0);
      local_44 = *(undefined4 *)(param_1 + 0x2dd4);
      (**(code **)(*(int *)(param_1 + 4) + 4))(*(undefined4 *)(param_1 + 4),&local_48);
      *(int *)(param_1 + 0x2dd0) = local_40;
      *(int *)(param_1 + 0x2dd4) = local_3c;
    }
  }
  if (cVar3 != '\0') {
    *param_3 = local_50;
    param_3[1] = iStack_4c;
  }
  return;
}

