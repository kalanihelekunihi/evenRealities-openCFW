
undefined4 td_session_find_by_id(int param_1,int param_2,short *param_3)

{
  ushort uVar1;
  short sVar2;
  
  if ((((param_1 != 0) && (param_3 != (short *)0x0)) && (param_2 != 0)) &&
     (*(short *)(param_1 + 0x8500) != 0)) {
    for (sVar2 = *(short *)(param_1 + 0x8500); sVar2 != 0; sVar2 = sVar2 + -1) {
      uVar1 = td_ring_index_wrap(param_1,sVar2 + -1);
      if (*(int *)((uint)uVar1 * 0x214 + param_1 + 0x208) == param_2) {
        *param_3 = sVar2 + -1;
        return 1;
      }
    }
  }
  return 0;
}

