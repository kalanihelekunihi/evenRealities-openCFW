
void FUN_00522920(undefined4 *param_1,int param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  
  FUN_00514846(0xc4,param_3);
  for (; param_2 != 0; param_2 = param_2 + -1) {
    FUN_00514846(200,*param_1);
    puVar1 = param_1 + 1;
    param_1 = param_1 + 2;
    FUN_00514846(0xcc,*puVar1);
  }
  return;
}

