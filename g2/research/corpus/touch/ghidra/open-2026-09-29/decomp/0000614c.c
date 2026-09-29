
void touch_sub_2e4c(int param_1)

{
  code *pcVar1;
  
  *(uint *)(*(int *)(param_1 + 4) + 8) = *(uint *)(*(int *)(param_1 + 4) + 8) & 0xfffffffe;
  *(uint *)(*(int *)(param_1 + 4) + 8) = *(uint *)(*(int *)(param_1 + 4) + 8) & 0xffffff7f;
  pcVar1 = *(code **)(*(int *)(param_1 + 8) + 4);
  if (pcVar1 != (code *)0x0) {
    (*pcVar1)(0);
  }
  return;
}

