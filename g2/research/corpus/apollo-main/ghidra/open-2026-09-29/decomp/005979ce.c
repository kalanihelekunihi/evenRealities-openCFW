
int td_session_ring_append(char param_1,undefined1 *param_2)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  undefined1 uVar4;
  int iVar5;
  
  iVar2 = DAT_00597be0;
  if (*(int *)(DAT_00597be0 + 0x8504) == 0) {
    td_session_ring_reset();
  }
  if ((param_1 == '\0') || (*(short *)(iVar2 + 0x8500) == 0)) {
    if (*(ushort *)(iVar2 + 0x8500) < 0x40) {
      uVar1 = td_ring_index_wrap(iVar2,*(undefined2 *)(iVar2 + 0x8500));
      *(short *)(iVar2 + 0x8500) = *(short *)(iVar2 + 0x8500) + 1;
      uVar4 = 2;
      param_1 = '\0';
    }
    else {
      uVar1 = *(ushort *)(iVar2 + 0x8502);
      *(ushort *)(iVar2 + 0x8502) = *(short *)(iVar2 + 0x8502) + 1U & 0x3f;
      uVar4 = 2;
      param_1 = '\0';
    }
  }
  else {
    uVar1 = td_ring_index_wrap(iVar2,*(short *)(iVar2 + 0x8500) + -1);
    uVar4 = 3;
  }
  iVar5 = iVar2 + (uint)uVar1 * 0x214;
  FUN_0043c0e4(iVar5,0x214,0);
  *(undefined4 *)(iVar5 + 0x20c) = *(undefined4 *)(iVar2 + 0x8504);
  if (param_1 == '\0') {
    iVar3 = *(int *)(iVar2 + 0x8508);
    *(int *)(iVar2 + 0x8508) = iVar3 + 1;
    *(int *)(iVar5 + 0x210) = iVar3;
  }
  else {
    if (*(int *)(iVar2 + 0x8508) == 0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *(int *)(iVar2 + 0x8508) + -1;
    }
    *(int *)(iVar5 + 0x210) = iVar2;
  }
  if (param_2 != (undefined1 *)0x0) {
    *param_2 = uVar4;
  }
  return iVar5;
}

