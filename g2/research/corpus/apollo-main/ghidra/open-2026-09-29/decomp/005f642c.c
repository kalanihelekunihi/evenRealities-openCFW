
void Ins_SHC(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  short sVar1;
  ushort uVar2;
  int iVar3;
  ushort uVar4;
  ushort local_44 [2];
  undefined4 local_40;
  undefined4 local_3c;
  undefined1 auStack_38 [16];
  int local_28;
  undefined4 uStack_14;
  
  if (*(short *)(param_1 + 0x160) == 0) {
    uVar2 = 1;
  }
  else {
    uVar2 = *(ushort *)(param_1 + 0x76);
  }
  sVar1 = (short)*param_2;
  if ((*param_2 & 0xffff) < (uint)uVar2) {
    uStack_14 = param_4;
    iVar3 = Compute_Point_Displacement(param_1,&local_3c,&local_40,auStack_38,local_44);
    if (iVar3 == 0) {
      if (sVar1 == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = (*(short *)(*(int *)(param_1 + 0x88) + sVar1 * 2 + -2) + 1) -
                *(short *)(param_1 + 0x8c);
      }
      if (*(short *)(param_1 + 0x160) == 0) {
        uVar4 = *(ushort *)(param_1 + 0x74);
      }
      else {
        uVar4 = (*(short *)(*(int *)(param_1 + 0x88) + sVar1 * 2) - *(short *)(param_1 + 0x8c)) + 1;
      }
      for (; uVar2 < uVar4; uVar2 = uVar2 + 1) {
        if ((local_28 != *(int *)(param_1 + 0x7c)) || (local_44[0] != uVar2)) {
          Move_Zp2_Point(param_1,uVar2,local_3c,local_40,1);
        }
      }
    }
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return;
}

