
uint td_ring_index_wrap(int param_1,ushort param_2)

{
  return ((uint)param_2 + (uint)*(ushort *)(param_1 + 0x8502)) % 0x40;
}

