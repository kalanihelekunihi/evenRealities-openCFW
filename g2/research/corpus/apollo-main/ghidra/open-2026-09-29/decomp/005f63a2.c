
void Ins_SHP(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined1 auStack_3c [4];
  undefined4 local_38;
  undefined4 local_34;
  undefined1 auStack_30 [36];
  undefined4 uStack_c;
  
  if (*(int *)(param_1 + 0x10) < *(int *)(param_1 + 0x134)) {
    if (*(char *)(param_1 + 0x235) != '\0') {
      *(undefined4 *)(param_1 + 0xc) = 0x86;
    }
  }
  else {
    uStack_c = param_4;
    iVar1 = Compute_Point_Displacement(param_1,&local_34,&local_38,auStack_30,auStack_3c);
    if (iVar1 != 0) {
      return;
    }
    while (0 < *(int *)(param_1 + 0x134)) {
      *(int *)(param_1 + 0x1c) = *(int *)(param_1 + 0x1c) + -1;
      uVar2 = *(uint *)(*(int *)(param_1 + 0x18) + *(int *)(param_1 + 0x1c) * 4);
      if ((uVar2 & 0xffff) < (uint)*(ushort *)(param_1 + 0x74)) {
        Move_Zp2_Point(param_1,uVar2 & 0xffff,local_34,local_38,1);
      }
      else if (*(char *)(param_1 + 0x235) != '\0') {
        *(undefined4 *)(param_1 + 0xc) = 0x86;
        return;
      }
      *(int *)(param_1 + 0x134) = *(int *)(param_1 + 0x134) + -1;
    }
  }
  *(undefined4 *)(param_1 + 0x134) = 1;
  *(undefined4 *)(param_1 + 0x20) = *(undefined4 *)(param_1 + 0x1c);
  return;
}

