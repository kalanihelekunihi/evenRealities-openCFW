
undefined4 FUN_00450dd4(int *param_1,int *param_2,int param_3,undefined4 param_4)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int local_28;
  int local_24;
  int local_20;
  int local_1c;
  undefined4 uStack_18;
  
  bVar1 = false;
  if (*param_1 <= *param_2) {
    if (*param_2 <= param_1[2]) {
      if (param_1[1] <= param_2[1]) {
        if (param_2[1] <= param_1[3]) {
          bVar1 = true;
        }
      }
    }
  }
  if (bVar1) {
    if (param_3 < 1) {
      uVar2 = 1;
    }
    else {
      uStack_18 = param_4;
      iVar3 = FUN_00451598(param_1);
      iVar4 = FUN_004515a4(param_1);
      iVar5 = iVar3 / 2;
      if (iVar4 / 2 <= iVar3 / 2) {
        iVar5 = iVar4 / 2;
      }
      if (iVar5 < param_3) {
        param_3 = iVar5;
      }
      local_28 = *param_1;
      local_20 = param_3 + *param_1;
      local_24 = param_1[1];
      local_1c = param_3 + param_1[1];
      iVar5 = FUN_00450dd4(&local_28,param_2,0);
      if (iVar5 == 0) {
        local_24 = param_1[3] - param_3;
        local_1c = param_1[3];
        iVar5 = FUN_00450dd4(&local_28,param_2,0);
        if (iVar5 == 0) {
          local_28 = param_1[2] - param_3;
          local_20 = param_1[2];
          iVar5 = FUN_00450dd4(&local_28,param_2,0);
          if (iVar5 == 0) {
            local_24 = param_1[1];
            local_1c = param_3 + param_1[1];
            iVar5 = FUN_00450dd4(&local_28,param_2,0);
            if (iVar5 == 0) {
              uVar2 = 1;
            }
            else {
              local_28 = local_28 - param_3;
              local_1c = param_3 + local_1c;
              uVar2 = FUN_0045163c(&local_28,param_2);
            }
          }
          else {
            local_28 = local_28 - param_3;
            local_24 = local_24 - param_3;
            uVar2 = FUN_0045163c(&local_28,param_2);
          }
        }
        else {
          local_20 = param_3 + local_20;
          local_24 = local_24 - param_3;
          uVar2 = FUN_0045163c(&local_28,param_2);
        }
      }
      else {
        local_20 = param_3 + local_20;
        local_1c = param_3 + local_1c;
        uVar2 = FUN_0045163c(&local_28,param_2);
      }
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

