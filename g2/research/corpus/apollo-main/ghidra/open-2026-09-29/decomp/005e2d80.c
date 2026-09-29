
undefined8 smpScActPkKeypress(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  ushort local_10;
  undefined1 local_e;
  undefined1 local_d;
  undefined4 local_c;
  
  local_10 = (ushort)param_3;
  local_e = (undefined1)((uint)param_3 >> 0x10);
  local_d = (undefined1)((uint)param_3 >> 0x18);
  pcVar1 = (char *)(*(int *)(param_2 + 4) + 8);
  if (*pcVar1 == '\x0e') {
    local_c = CONCAT31((int3)((uint)param_4 >> 8),*(undefined1 *)(*(int *)(param_2 + 4) + 9));
    local_10 = (ushort)*(byte *)(param_1 + 0x3d);
    local_e = 0x36;
    local_d = 0;
    DmSmpCbackExec(&local_10);
  }
  else {
    local_c = param_4;
    if (*pcVar1 == '\x03') {
      *(undefined1 *)(param_2 + 2) = 0x1e;
      *(undefined1 *)(param_2 + 3) = 0;
      smpSmExecute();
    }
  }
  return CONCAT44(local_c,CONCAT13(local_d,CONCAT12(local_e,local_10)));
}

