
uint attSetMtu(int param_1,byte param_2,uint param_3,uint param_4)

{
  undefined4 local_10;
  
  if ((param_4 & 0xffff) <= (param_3 & 0xffff)) {
    param_3 = param_4;
  }
  local_10 = param_4;
  if ((uint)*(ushort *)(param_1 + (uint)param_2 * 4) != (param_3 & 0xffff)) {
    *(short *)(param_1 + (uint)param_2 * 4) = (short)param_3;
    local_10 = param_3 & 0xffff;
    attExecCallback(*(undefined1 *)(param_1 + 0xe),0x16,0,0);
  }
  return local_10;
}

