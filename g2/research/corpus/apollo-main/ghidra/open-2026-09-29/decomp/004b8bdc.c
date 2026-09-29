
void tpl_context_mark_packet_004b8bdc(int param_1,byte param_2)

{
  *(byte *)((uint)(param_2 >> 3) + param_1 + 0x10) =
       (byte)(1 << (uint)param_2 % 8) | *(byte *)((uint)(param_2 >> 3) + param_1 + 0x10);
  *(char *)(param_1 + 0x31) = *(char *)(param_1 + 0x31) + '\x01';
  return;
}

