
void FUN_00488cda(int *param_1,int param_2,int param_3,int param_4,short param_5,short param_6,
                 undefined4 param_7)

{
  int iVar1;
  int iVar2;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  int local_2c;
  int iStack_28;
  
  if (((param_4 == 0) && (param_5 == 0x100)) && (param_6 == 0x100)) {
    *param_1 = 0;
    param_1[1] = 0;
    param_1[2] = param_2 + -1;
    param_1[3] = param_3 + -1;
  }
  else {
    iStack_28 = param_4;
    FUN_0048949c(&local_48,0x20);
    local_40 = param_2;
    local_34 = param_3;
    local_30 = param_2;
    local_2c = param_3;
    FUN_004513ae(&local_48,param_4,param_5,param_6,param_7,1);
    FUN_004513ae(&local_40,param_4,param_5,param_6,param_7,1);
    FUN_004513ae(&local_38,param_4,param_5,param_6,param_7,1);
    FUN_004513ae(&local_30,param_4,param_5,param_6,param_7,1);
    iVar1 = local_40;
    if (local_48 < local_40) {
      iVar1 = local_48;
    }
    iVar2 = local_30;
    if (local_38 < local_30) {
      iVar2 = local_38;
    }
    if (iVar1 < iVar2) {
      iVar1 = local_40;
      if (local_48 < local_40) {
        iVar1 = local_48;
      }
    }
    else {
      iVar1 = local_30;
      if (local_38 < local_30) {
        iVar1 = local_38;
      }
    }
    *param_1 = iVar1;
    iVar1 = local_30;
    if (local_30 < local_38) {
      iVar1 = local_38;
    }
    iVar2 = local_40;
    if (local_40 < local_48) {
      iVar2 = local_48;
    }
    if (iVar1 < iVar2) {
      local_30 = local_40;
      if (local_40 < local_48) {
        local_30 = local_48;
      }
    }
    else if (local_30 < local_38) {
      local_30 = local_38;
    }
    param_1[2] = local_30 + -1;
    iVar1 = local_3c;
    if (local_44 < local_3c) {
      iVar1 = local_44;
    }
    iVar2 = local_2c;
    if (local_34 < local_2c) {
      iVar2 = local_34;
    }
    if (iVar1 < iVar2) {
      iVar1 = local_3c;
      if (local_44 < local_3c) {
        iVar1 = local_44;
      }
    }
    else {
      iVar1 = local_2c;
      if (local_34 < local_2c) {
        iVar1 = local_34;
      }
    }
    param_1[1] = iVar1;
    iVar1 = local_2c;
    if (local_2c < local_34) {
      iVar1 = local_34;
    }
    iVar2 = local_3c;
    if (local_3c < local_44) {
      iVar2 = local_44;
    }
    if (iVar1 < iVar2) {
      local_2c = local_3c;
      if (local_3c < local_44) {
        local_2c = local_44;
      }
    }
    else if (local_2c < local_34) {
      local_2c = local_34;
    }
    param_1[3] = local_2c + -1;
  }
  return;
}

