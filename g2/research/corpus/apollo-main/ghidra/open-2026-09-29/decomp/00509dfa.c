
undefined4 ui_common_api_fn_00509dfa(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 0xfffffffc;
  }
  else if (*(short *)(param_1 + 0x204) == 0) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

