
void even_ai_node_stream_state_init(int param_1,char param_2,ushort param_3)

{
  ushort uVar1;
  
  if (param_1 != 0) {
    if (param_2 == '\0') {
      uVar1 = *(ushort *)(param_1 + 0x1a);
      *(ushort *)(param_1 + 0x1a) = param_3;
      if ((uint)*(ushort *)(DAT_004e64a8 + 0x1e) + (uint)param_3 < (uint)uVar1) {
        *(undefined2 *)(DAT_004e64a8 + 0x1e) = 0;
      }
      else {
        *(ushort *)(DAT_004e64a8 + 0x1e) = (param_3 + *(short *)(DAT_004e64a8 + 0x1e)) - uVar1;
      }
    }
    else {
      uVar1 = *(ushort *)(param_1 + 0x18);
      *(ushort *)(param_1 + 0x18) = param_3;
      if ((uint)*(ushort *)(DAT_004e64a8 + 0x1c) + (uint)param_3 < (uint)uVar1) {
        *(undefined2 *)(DAT_004e64a8 + 0x1c) = 0;
      }
      else {
        *(ushort *)(DAT_004e64a8 + 0x1c) = (param_3 + *(short *)(DAT_004e64a8 + 0x1c)) - uVar1;
      }
    }
    if ((uint)*(ushort *)(DAT_004e64a8 + 0x1a) + (uint)param_3 < (uint)uVar1) {
      *(undefined2 *)(DAT_004e64a8 + 0x1a) = 0;
    }
    else {
      *(ushort *)(DAT_004e64a8 + 0x1a) = (param_3 + *(short *)(DAT_004e64a8 + 0x1a)) - uVar1;
    }
  }
  return;
}

