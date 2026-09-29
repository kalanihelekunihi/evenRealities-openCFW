
void smpAuthReq(int param_1,undefined1 param_2,undefined1 param_3)

{
  ushort local_20;
  undefined1 local_1e;
  undefined1 local_1c;
  undefined1 local_1b;
  undefined1 local_1a;
  undefined1 local_c;
  
  if ((int)((uint)*(byte *)(param_1 + 0x40) << 0x1d) < 0) {
    local_20 = (ushort)*(byte *)(param_1 + 0x3d);
    local_1e = 0x2e;
    local_1c = param_2;
    local_1b = param_3;
    DmSmpCbackExec(&local_20);
  }
  else {
    local_20 = (ushort)*(byte *)(param_1 + 0x3d);
    local_1e = 4;
    local_1c = 0;
    local_1b = 0;
    local_1a = 0;
    local_c = 3;
    smpSmExecute(param_1,&local_20);
  }
  return;
}

