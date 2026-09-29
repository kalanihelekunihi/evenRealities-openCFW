
void Ins_FLIPRGOFF(int *param_1,uint *param_2)

{
  uint uVar1;
  uint uVar2;
  
  if ((((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) != 0x28) ||
       (*(char *)((int)param_1 + 0x267) == '\0')) || ((char)param_1[0x9a] == '\0')) ||
     (*(char *)((int)param_1 + 0x269) == '\0')) {
    uVar2 = param_2[1];
    uVar1 = *param_2;
    if (((uVar2 & 0xffff) < (uint)*(ushort *)(param_1 + 0x26)) &&
       ((uVar1 & 0xffff) < (uint)*(ushort *)(param_1 + 0x26))) {
      for (; (uVar1 & 0xffff) <= (uVar2 & 0xffff); uVar1 = uVar1 + 1) {
        *(byte *)(param_1[0x2a] + (uVar1 & 0xffff)) =
             *(byte *)(param_1[0x2a] + (uVar1 & 0xffff)) & 0xfe;
      }
    }
    else if (*(char *)((int)param_1 + 0x235) != '\0') {
      param_1[3] = 0x86;
    }
  }
  return;
}

