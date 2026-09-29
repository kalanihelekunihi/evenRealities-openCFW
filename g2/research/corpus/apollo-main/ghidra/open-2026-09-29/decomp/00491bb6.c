
undefined4 FUN_00491bb6(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 uVar1;
  
  uVar1 = FUN_0049172c();
  *(undefined2 *)(param_1 + 0x601a) = uVar1;
  uVar1 = FUN_00491730(*(undefined2 *)(param_1 + 0x601a),1);
  *(undefined2 *)(param_1 + 0x601a) = uVar1;
  *(undefined1 *)(param_1 + 0x6020) = 0;
  *(undefined1 *)(param_1 + 0x10) = 3;
  *(undefined2 *)(param_1 + 0x6018) = 0;
  return param_4;
}

