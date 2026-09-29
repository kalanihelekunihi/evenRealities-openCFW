
undefined4 td_ring_write(ushort *param_1)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  iVar1 = DAT_00597c08;
  if (param_1 == (ushort *)0x0) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar4 = (uint)*(ushort *)(DAT_00597c08 + 0x800);
    if (*(ushort *)(DAT_00597c08 + 0x802) < uVar4) {
      uVar4 = (uint)*(ushort *)(DAT_00597c08 + 0x802);
    }
    if (0x7ff < uVar4) {
      uVar4 = 0x7ff;
    }
    if ((*(char *)((int)param_1 + 0x203) == '\0') || (*param_1 != 0)) {
      uVar3 = (uint)*param_1;
      if (0x7ff - uVar4 < uVar3) {
        uVar3 = 0x7ff - uVar4;
      }
      if (uVar3 != 0) {
        FUN_00439be4(DAT_00597c08 + uVar4,param_1 + 1,uVar3);
      }
      *(short *)(iVar1 + 0x802) = (short)uVar3 + (short)uVar4;
      *(undefined1 *)(iVar1 + (uint)*(ushort *)(iVar1 + 0x802)) = 0;
      if ((char)param_1[0x101] != '\0') {
        *(undefined2 *)(iVar1 + 0x800) = *(undefined2 *)(iVar1 + 0x802);
      }
      if (*(ushort *)(iVar1 + 0x802) < *(ushort *)(iVar1 + 0x800)) {
        *(undefined2 *)(iVar1 + 0x800) = *(undefined2 *)(iVar1 + 0x802);
      }
      *(bool *)(iVar1 + 0x804) = (char)param_1[0x101] != '\0';
      *(bool *)(iVar1 + 0x805) = *(char *)((int)param_1 + 0x203) != '\0';
      uVar2 = 0;
    }
    else {
      if (0x7ff < *(ushort *)(DAT_00597c08 + 0x802)) {
        *(undefined2 *)(DAT_00597c08 + 0x802) = 0x7ff;
      }
      *(undefined1 *)(iVar1 + (uint)*(ushort *)(iVar1 + 0x802)) = 0;
      if ((char)param_1[0x101] != '\0') {
        *(undefined2 *)(iVar1 + 0x800) = *(undefined2 *)(iVar1 + 0x802);
      }
      *(bool *)(iVar1 + 0x804) = (char)param_1[0x101] != '\0';
      *(undefined1 *)(iVar1 + 0x805) = 1;
      uVar2 = 0;
    }
  }
  return uVar2;
}

