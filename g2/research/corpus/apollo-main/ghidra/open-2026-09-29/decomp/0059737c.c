
int td_session_record_at(ushort param_1)

{
  ushort uVar1;
  int iVar2;
  
  iVar2 = DAT_00597be0;
  if (param_1 < *(ushort *)(DAT_00597be0 + 0x8500)) {
    uVar1 = td_ring_index_wrap(DAT_00597be0,param_1);
    iVar2 = (uint)uVar1 * 0x214 + iVar2;
  }
  else {
    iVar2 = 0;
  }
  return iVar2;
}

