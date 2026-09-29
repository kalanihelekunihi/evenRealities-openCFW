
void FUN_00557f4a(undefined4 param_1,undefined4 param_2,undefined4 *param_3,int param_4,char param_5
                 )

{
  int local_78;
  undefined4 local_74;
  undefined4 local_68;
  undefined4 local_48;
  int iStack_18;
  
  iStack_18 = param_4;
  if (param_5 == '\0') {
    FUN_00450500(param_4,0);
    *(undefined4 *)(param_4 + 0xc) = 0xffffffff;
    *param_3 = param_2;
    FUN_00440656(param_1);
    FUN_00450500(param_4,0);
    FUN_0055801c(param_1,param_4);
  }
  else {
    if (*(int *)(param_4 + 0xc) == -1) {
      *(undefined4 *)(param_4 + 4) = *param_3;
      *(undefined4 *)(param_4 + 8) = param_2;
    }
    else {
      *(undefined4 *)(param_4 + 4) = *(undefined4 *)(param_4 + 8);
      *(undefined4 *)(param_4 + 8) = param_2;
    }
    *param_3 = param_2;
    FUN_00450500(param_4,0);
    FUN_004503d6(&local_78);
    local_74 = DAT_00558014;
    local_78 = param_4;
    FUN_004506ce(&local_78,0,0x100);
    local_68 = DAT_00558018;
    local_48 = FUN_00557508(param_1,0);
    FUN_00450408(&local_78);
  }
  return;
}

