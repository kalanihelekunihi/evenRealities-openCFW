
void FUN_0053f400(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined1 auStack_80 [28];
  int local_64;
  undefined4 uStack_14;
  
  piVar1 = *(int **)(param_2 + 0x1c);
  if (*piVar1 != 0) {
    uStack_14 = param_4;
    FUN_00439c04(auStack_80,param_2,0x6c);
    local_64 = *piVar1;
    FUN_0053f42a(param_1,auStack_80,param_3);
  }
  return;
}

