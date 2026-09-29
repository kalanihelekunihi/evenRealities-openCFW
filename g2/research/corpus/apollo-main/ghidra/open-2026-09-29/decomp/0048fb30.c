
undefined4 FUN_0048fb30(int param_1,char param_2,int *param_3)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 local_40;
  undefined1 auStack_3c [8];
  uint local_34;
  int local_30;
  undefined1 auStack_2c [12];
  undefined1 auStack_20 [16];
  
  if (*(int *)(*param_3 + 0xc) == 0) {
    uVar2 = FUN_0048f6a0(param_1,param_2);
  }
  else if (param_2 == '\x02') {
    iVar3 = FUN_0048f77e(param_1,auStack_3c);
    if (iVar3 == 0) {
      uVar2 = 0;
    }
    else {
      do {
        uVar1 = local_34;
        iVar3 = (**(code **)(*param_3 + 0xc))(auStack_3c,0,param_3);
        if (iVar3 == 0) {
          if (*(int *)(param_1 + 0xc) == 0) {
            iVar3 = DAT_004905b0;
            if (local_30 != 0) {
              iVar3 = local_30;
            }
          }
          else {
            iVar3 = *(int *)(param_1 + 0xc);
          }
          *(int *)(param_1 + 0xc) = iVar3;
          return 0;
        }
      } while ((local_34 != 0) && (local_34 < uVar1));
      iVar3 = FUN_0048f7ca(param_1,auStack_3c);
      if (iVar3 == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = 1;
      }
    }
  }
  else {
    local_40 = 10;
    iVar3 = FUN_0048f6ea(param_1,param_2,auStack_2c,&local_40);
    if (iVar3 == 0) {
      uVar2 = 0;
    }
    else {
      FUN_0048f49c(auStack_20,auStack_2c,local_40);
      uVar2 = (**(code **)(*param_3 + 0xc))(auStack_20,0,param_3);
    }
  }
  return uVar2;
}

