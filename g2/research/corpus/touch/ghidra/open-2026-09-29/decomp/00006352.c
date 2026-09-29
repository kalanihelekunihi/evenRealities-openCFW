
uint touch_sub_3052(int *param_1,int param_2)

{
  uint uVar1;
  undefined4 uVar2;
  
  if (*(char *)((int)param_1 + 0x7a) == '\x01') {
    uVar2 = 8;
  }
  else if (*(char *)((int)param_1 + 0x7a) == '\n') {
    uVar2 = 8;
  }
  else {
    uVar2 = 0;
  }
  uVar1 = touch_sub_3030(*(undefined2 *)(*param_1 + 0xe),uVar2,*(undefined1 *)((int)param_1 + 0x87),
                         *(undefined1 *)(*(int *)(param_2 + 8) + 0x4e));
  return uVar1 | 0x80;
}

