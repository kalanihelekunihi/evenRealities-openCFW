
bool tpl_context_packet_seen_004b8c14(int param_1,byte param_2)

{
  return ((uint)*(byte *)(param_1 + (uint)(param_2 >> 3) + 0x10) & 1 << (uint)param_2 % 8) != 0;
}

