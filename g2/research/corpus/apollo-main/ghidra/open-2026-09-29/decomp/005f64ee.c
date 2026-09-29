
void Ins_SHZ(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  ushort uVar2;
  ushort uVar3;
  ushort local_44 [2];
  undefined4 local_40;
  undefined4 local_3c;
  undefined1 auStack_38 [16];
  int local_28;
  undefined4 uStack_14;
  
  if (*param_2 < 2) {
    uStack_14 = param_4;
    iVar1 = Compute_Point_Displacement(param_1,&local_3c,&local_40,auStack_38,local_44);
    if (iVar1 == 0) {
      if (*(short *)(param_1 + 0x160) == 0) {
        uVar2 = *(ushort *)(param_1 + 0x74);
      }
      else if ((*(short *)(param_1 + 0x160) == 1) && (0 < *(short *)(param_1 + 0x76))) {
        uVar2 = *(short *)(*(int *)(param_1 + 0x88) + *(short *)(param_1 + 0x76) * 2 + -2) + 1;
      }
      else {
        uVar2 = 0;
      }
      for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1) {
        if ((local_28 != *(int *)(param_1 + 0x7c)) || (local_44[0] != uVar3)) {
          Move_Zp2_Point(param_1,uVar3,local_3c,local_40,0);
        }
      }
    }
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return;
}

