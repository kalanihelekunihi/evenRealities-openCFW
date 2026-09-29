
void Ins_GETINFO(int *param_1,uint *param_2)

{
  uint uVar1;
  
  uVar1 = 0;
  if ((int)((uint)(byte)*param_2 << 0x1f) < 0) {
    uVar1 = *(uint *)(*(int *)(*param_1 + 0x60) + 0x40);
  }
  if (((int)((uint)(byte)*param_2 << 0x1e) < 0) && (*(char *)((int)param_1 + 0x11d) != '\0')) {
    uVar1 = uVar1 | 0x100;
  }
  if (((int)((uint)(byte)*param_2 << 0x1d) < 0) && (*(char *)((int)param_1 + 0x11e) != '\0')) {
    uVar1 = uVar1 | 0x200;
  }
  if (((int)((uint)(byte)*param_2 << 0x1c) < 0) && (*(int *)(*param_1 + 700) != 0)) {
    uVar1 = uVar1 | 0x400;
  }
  if (((int)((uint)(byte)*param_2 << 0x1a) < 0) && ((char)param_1[0x99] != '\0')) {
    uVar1 = uVar1 | 0x1000;
  }
  if ((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x28) &&
     (*(char *)((int)param_1 + 0x265) != '\0')) {
    if ((int)((uint)(byte)*param_2 << 0x19) < 0) {
      uVar1 = uVar1 | 0x2000;
    }
    if (((int)(*param_2 << 0x17) < 0) && (*(char *)((int)param_1 + 0x266) != '\0')) {
      uVar1 = uVar1 | 0x8000;
    }
    if ((int)(*param_2 << 0x15) < 0) {
      uVar1 = uVar1 | 0x20000;
    }
    if (((int)(*param_2 << 0x14) < 0) && (*(char *)((int)param_1 + 0x265) != '\0')) {
      uVar1 = uVar1 | 0x40000;
    }
    if (((int)(*param_2 << 0x13) < 0) && (*(char *)((int)param_1 + 0x26a) != '\0')) {
      uVar1 = uVar1 | 0x80000;
    }
  }
  *param_2 = uVar1;
  return;
}

