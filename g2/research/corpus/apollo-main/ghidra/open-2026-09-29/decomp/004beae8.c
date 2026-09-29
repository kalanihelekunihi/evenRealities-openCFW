
void AnccGetNotificationAttribute
               (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 local_20;
  undefined1 local_1f;
  undefined1 local_1e;
  undefined1 local_1d;
  undefined1 local_1c;
  undefined1 local_1b;
  undefined1 local_1a;
  undefined1 local_19;
  undefined1 local_18;
  undefined1 local_17;
  undefined1 local_16;
  undefined1 local_15;
  undefined1 local_14;
  undefined1 local_13;
  undefined1 local_12;
  undefined1 local_11;
  undefined1 local_10;
  undefined1 local_f;
  undefined1 local_e;
  undefined4 uStack_c;
  
  if (*(short *)(param_1 + 4) != 0) {
    local_20 = 0;
    local_1f = (undefined1)param_2;
    local_1e = (undefined1)((uint)param_2 >> 8);
    local_1d = (undefined1)((uint)param_2 >> 0x10);
    local_1c = (undefined1)((uint)param_2 >> 0x18);
    local_1b = 0;
    local_1a = 1;
    local_19 = 0;
    local_18 = 1;
    local_17 = 2;
    local_16 = 0;
    local_15 = 1;
    local_14 = 3;
    local_13 = 0;
    local_12 = 1;
    local_11 = 4;
    local_10 = 5;
    local_f = 6;
    local_e = 7;
    uStack_c = param_4;
    AttcWriteReq(*DAT_004bf6c0,*(undefined2 *)(param_1 + 4),0x13,&local_20);
  }
  return;
}

