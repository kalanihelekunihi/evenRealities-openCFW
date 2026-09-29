
void FUN_00550ef4(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_50;
  undefined4 local_40;
  
  iVar1 = DAT_00550ff4;
  if ((*(int *)(DAT_00550ff4 + 0xc) != 0) && (0 < param_1)) {
    if (param_1 < 4) {
      FUN_0044ea04(*(undefined4 *)(DAT_00550ff4 + 0xc),0,0);
    }
    else {
      if (param_2 < 1) {
        param_1 = 0;
      }
      else if (param_2 < param_1 + -1) {
        param_1 = param_2 + -1;
      }
      else {
        param_1 = param_1 + -3;
      }
      FUN_004503d6(&local_70);
      local_70 = *(undefined4 *)(iVar1 + 0xc);
      uVar2 = FUN_0044e498(*(undefined4 *)(iVar1 + 0xc));
      FUN_004506ce(&local_70,uVar2,param_1 * 0xc);
      local_6c = DAT_00551aa0;
      local_50 = DAT_005511b8;
      local_40 = param_3;
      FUN_00450408(&local_70);
    }
  }
  return;
}

