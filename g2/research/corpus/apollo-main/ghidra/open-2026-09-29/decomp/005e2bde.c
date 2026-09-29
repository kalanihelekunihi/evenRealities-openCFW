
void smpScActPkSetup(int param_1)

{
  ushort local_20;
  undefined1 local_1e;
  undefined1 local_1c;
  undefined1 local_1b;
  
  *(undefined1 *)(*(int *)(param_1 + 0x48) + 3) = 0;
  *(undefined1 *)(param_1 + 0x3f) = 3;
  local_20 = (ushort)*(byte *)(param_1 + 0x3d);
  local_1e = 0x2e;
  local_1c = 0;
  local_1b = *(undefined1 *)(*(int *)(param_1 + 0x48) + 4);
  DmSmpCbackExec(&local_20);
  return;
}

