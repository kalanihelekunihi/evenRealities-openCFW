
void even_ai_node_stream_state_update(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_004e64a8;
  if (param_1 != 0) {
    if ((uint)*(ushort *)(param_1 + 0x1a) + (uint)*(ushort *)(param_1 + 0x18) <
        (uint)*(ushort *)(DAT_004e64a8 + 0x1a)) {
      *(short *)(DAT_004e64a8 + 0x1a) =
           (*(short *)(DAT_004e64a8 + 0x1a) - *(short *)(param_1 + 0x18)) -
           *(short *)(param_1 + 0x1a);
    }
    else {
      *(undefined2 *)(DAT_004e64a8 + 0x1a) = 0;
    }
    if (*(ushort *)(param_1 + 0x18) < *(ushort *)(iVar1 + 0x1c)) {
      *(short *)(iVar1 + 0x1c) = *(short *)(iVar1 + 0x1c) - *(short *)(param_1 + 0x18);
    }
    else {
      *(undefined2 *)(iVar1 + 0x1c) = 0;
    }
    if (*(ushort *)(param_1 + 0x1a) < *(ushort *)(iVar1 + 0x1e)) {
      *(short *)(iVar1 + 0x1e) = *(short *)(iVar1 + 0x1e) - *(short *)(param_1 + 0x1a);
    }
    else {
      *(undefined2 *)(iVar1 + 0x1e) = 0;
    }
    *(undefined2 *)(param_1 + 0x18) = 0;
    *(undefined2 *)(param_1 + 0x1a) = 0;
  }
  return;
}

