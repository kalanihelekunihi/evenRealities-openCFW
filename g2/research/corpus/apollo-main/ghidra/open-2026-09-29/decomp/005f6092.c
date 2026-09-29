
void Ins_FLIPPT(int *param_1)

{
  uint uVar1;
  
  if ((((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) != 0x28) ||
       (*(char *)((int)param_1 + 0x267) == '\0')) || ((char)param_1[0x9a] == '\0')) ||
     (*(char *)((int)param_1 + 0x269) == '\0')) {
    if (param_1[4] < param_1[0x4d]) {
      if (*(char *)((int)param_1 + 0x235) != '\0') {
        param_1[3] = 0x81;
      }
    }
    else {
      while (0 < param_1[0x4d]) {
        param_1[7] = param_1[7] + -1;
        uVar1 = *(uint *)(param_1[6] + param_1[7] * 4);
        if ((uVar1 & 0xffff) < (uint)*(ushort *)(param_1 + 0x26)) {
          *(byte *)(param_1[0x2a] + (uVar1 & 0xffff)) =
               *(byte *)(param_1[0x2a] + (uVar1 & 0xffff)) ^ 1;
        }
        else if (*(char *)((int)param_1 + 0x235) != '\0') {
          param_1[3] = 0x86;
          return;
        }
        param_1[0x4d] = param_1[0x4d] + -1;
      }
    }
  }
  param_1[0x4d] = 1;
  param_1[8] = param_1[7];
  return;
}

