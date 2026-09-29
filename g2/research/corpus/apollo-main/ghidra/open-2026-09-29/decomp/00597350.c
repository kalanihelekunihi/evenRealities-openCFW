
int td_last_session_record(void)

{
  ushort uVar1;
  int iVar2;
  
  iVar2 = DAT_00597be0;
  if (*(short *)(DAT_00597be0 + 0x8500) == 0) {
    iVar2 = 0;
  }
  else {
    uVar1 = td_ring_index_wrap(DAT_00597be0,*(short *)(DAT_00597be0 + 0x8500) + -1);
    iVar2 = (uint)uVar1 * 0x214 + iVar2;
  }
  return iVar2;
}

