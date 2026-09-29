
undefined8
attcDiscDescriptors(undefined1 param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  ushort uVar2;
  int *piVar3;
  ushort uVar4;
  
  uVar4 = 0;
  uVar2 = 0;
  piVar3 = (int *)(*param_2 + (uint)*(byte *)((int)param_2 + 0x12) * 4);
  while (*(byte *)((int)param_2 + 0x12) < *(byte *)(param_2 + 3)) {
    if ((int)((uint)*(byte *)(*piVar3 + 4) << 0x1d) < 0) {
      uVar4 = *(short *)(param_2[1] + (uint)*(byte *)((int)param_2 + 0x12) * 2 + -2) + 1;
      uVar2 = *(ushort *)(param_2[1] + (uint)*(byte *)((int)param_2 + 0x12) * 2);
      *(undefined2 *)(param_2[1] + (uint)*(byte *)((int)param_2 + 0x12) * 2) = 0;
      if (uVar4 <= uVar2) break;
      while (*(char *)((int)param_2 + 0x12) = *(char *)((int)param_2 + 0x12) + '\x01',
            *(byte *)((int)param_2 + 0x12) < *(byte *)(param_2 + 3)) {
        piVar3 = piVar3 + 1;
      }
    }
    else {
      piVar3 = piVar3 + 1;
      *(char *)((int)param_2 + 0x12) = *(char *)((int)param_2 + 0x12) + '\x01';
    }
  }
  if (*(char *)((int)param_2 + 0x12) == (char)param_2[3]) {
    uVar1 = attcDiscVerify(param_2);
  }
  else {
    AttcFindInfoReq(param_1,uVar4,uVar2,1);
    uVar1 = 0x79;
  }
  return CONCAT44(param_4,uVar1);
}

