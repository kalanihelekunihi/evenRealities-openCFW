
undefined4 FUN_004d916e(int *param_1)

{
  ushort uVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  if (*(ushort *)(param_1 + 2) < *(ushort *)(*param_1 + 0x10)) {
    uVar3 = *(uint *)(*(int *)*param_1 + (uint)*(ushort *)((int)param_1 + 10) * 4);
    *(char *)((int)param_1 + 0x16) = (char)(uVar3 >> 8);
    uVar4 = uVar3 & 3;
    uVar1 = (ushort)(uVar3 >> 0x10);
    if (uVar4 == 0) {
      *(undefined2 *)(param_1 + 5) = 1;
      *(ushort *)(param_1 + 4) = (ushort)((uVar3 << 0x18) >> 0x1a);
      uVar4 = uVar3 >> 0x18 & 0xf;
      uVar5 = (uVar3 & 0xffffff) >> 0x10;
      *(ushort *)((int)param_1 + 0x12) = uVar1 >> 0xc;
    }
    else if (uVar4 == 2) {
      uVar4 = *(uint *)(*(int *)*param_1 + (uint)*(ushort *)((int)param_1 + 10) * 4 + 4);
      uVar5 = *(uint *)(*(int *)*param_1 + (uint)*(ushort *)((int)param_1 + 10) * 4 + 8);
      uVar2 = *(undefined4 *)(*(int *)*param_1 + (uint)*(ushort *)((int)param_1 + 10) * 4 + 0xc);
      *(ushort *)(param_1 + 5) = uVar1;
      *(ushort *)(param_1 + 4) = (ushort)((uVar3 << 0x18) >> 0x1a) | (ushort)((uVar4 >> 8) << 6);
      *(short *)((int)param_1 + 0x12) = (short)uVar2;
    }
    else if (uVar4 < 2) {
      uVar6 = *(uint *)(*(int *)*param_1 + (uint)*(ushort *)((int)param_1 + 10) * 4 + 4);
      *(ushort *)(param_1 + 5) = uVar1 & 0xfff;
      *(ushort *)(param_1 + 4) = (ushort)((uVar3 << 0x18) >> 0x1a) | (ushort)((uVar6 >> 0x1c) << 6);
      uVar4 = uVar3 >> 0x1c;
      uVar5 = uVar6 & 0xffff;
      *(ushort *)((int)param_1 + 0x12) = (ushort)(uVar6 >> 0x10) & 0xfff;
    }
    else {
      uVar4 = *(uint *)(*(int *)*param_1 + (uint)*(ushort *)((int)param_1 + 10) * 4 + 4);
      uVar5 = *(uint *)(*(int *)*param_1 + (uint)*(ushort *)((int)param_1 + 10) * 4 + 8);
      uVar2 = *(undefined4 *)(*(int *)*param_1 + (uint)*(ushort *)((int)param_1 + 10) * 4 + 0xc);
      *(short *)(param_1 + 5) =
           (short)*(undefined4 *)
                   (*(int *)*param_1 + (uint)*(ushort *)((int)param_1 + 10) * 4 + 0x10);
      *(ushort *)(param_1 + 4) = (ushort)((uVar3 << 0x18) >> 0x1a) | (ushort)((uVar4 >> 8) << 6);
      *(short *)((int)param_1 + 0x12) = (short)uVar2;
    }
    if (param_1[1] == 0) {
      param_1[6] = 0;
      param_1[8] = 0;
    }
    else {
      param_1[6] = param_1[1] + uVar5;
      if ((char)uVar4 == '\0') {
        if (((*(byte *)((int)param_1 + 0x16) & 0x30) == 0x20) &&
           (((*(byte *)((int)param_1 + 0x16) & 0xc0) == 0 ||
            ((*(byte *)((int)param_1 + 0x16) & 0xc0) == 0x80)))) {
          param_1[8] = (int)(param_1 + 5);
        }
        else {
          param_1[8] = 0;
        }
      }
      else {
        param_1[8] = param_1[6] - (int)(char)uVar4;
      }
      if (((*(byte *)((int)param_1 + 0x16) & 0xc0) == 0x80) && (param_1[6] != 0)) {
        param_1[7] = *(int *)param_1[6];
      }
      else {
        param_1[7] = param_1[6];
      }
    }
    if (((*(byte *)((int)param_1 + 0x16) & 0xf) == 8) ||
       ((*(byte *)((int)param_1 + 0x16) & 0xf) == 9)) {
      param_1[9] = *(int *)(*(int *)(*param_1 + 4) + (uint)*(ushort *)((int)param_1 + 0xe) * 4);
    }
    else {
      param_1[9] = 0;
    }
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

