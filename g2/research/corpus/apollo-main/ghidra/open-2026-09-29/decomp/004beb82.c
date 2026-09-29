
undefined8
AncsPerformNotiAction(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  undefined1 local_10;
  undefined1 local_f;
  undefined1 local_e;
  undefined1 local_d;
  undefined1 local_c;
  undefined1 local_b;
  undefined2 uStack_a;
  
  local_c = (undefined1)param_4;
  local_b = (undefined1)((uint)param_4 >> 8);
  uStack_a = (undefined2)((uint)param_4 >> 0x10);
  local_10 = (undefined1)param_3;
  uVar1 = local_10;
  local_f = (undefined1)((uint)param_3 >> 8);
  local_e = (undefined1)((uint)param_3 >> 0x10);
  local_d = (undefined1)((uint)param_3 >> 0x18);
  if (*(short *)(param_1 + 4) != 0) {
    local_10 = 2;
    local_f = (undefined1)param_2;
    local_e = (undefined1)((uint)param_2 >> 8);
    local_d = (undefined1)((uint)param_2 >> 0x10);
    local_c = (undefined1)((uint)param_2 >> 0x18);
    local_b = uVar1;
    AttcWriteReq(*DAT_004bf6c0,*(undefined2 *)(param_1 + 4),6,&local_10);
  }
  return CONCAT26(uStack_a,CONCAT15(local_b,CONCAT14(local_c,CONCAT13(local_d,CONCAT12(local_e,
                                                  CONCAT11(local_f,local_10))))));
}

