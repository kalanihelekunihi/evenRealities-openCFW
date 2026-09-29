
void TT_Run_Context(int *param_1)

{
  TT_Goto_CodeRange(param_1,3,0);
  FUN_00439c04(param_1 + 9,param_1 + 0x24,0x24);
  FUN_00439c04(param_1 + 0x12,param_1 + 0x24,0x24);
  FUN_00439c04(param_1 + 0x1b,param_1 + 0x24,0x24);
  *(undefined2 *)(param_1 + 0x57) = 1;
  *(undefined2 *)((int)param_1 + 0x15e) = 1;
  *(undefined2 *)(param_1 + 0x58) = 1;
  *(undefined2 *)((int)param_1 + 0x12a) = 0x4000;
  *(undefined2 *)(param_1 + 0x4b) = 0;
  *(undefined4 *)((int)param_1 + 0x12e) = *(undefined4 *)((int)param_1 + 0x12a);
  *(undefined4 *)((int)param_1 + 0x126) = *(undefined4 *)((int)param_1 + 0x12a);
  param_1[0x4f] = 1;
  param_1[0x4d] = 1;
  param_1[4] = 0;
  param_1[0x6c] = 0;
  (**(code **)(*param_1 + 0x2a0))(param_1);
  return;
}

