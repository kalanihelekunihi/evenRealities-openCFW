
undefined8 dmConn2ActAuthToExpired(int param_1,int param_2)

{
  undefined4 unaff_r6;
  ushort local_10;
  undefined1 local_e;
  undefined1 local_d;
  undefined2 local_c;
  undefined2 uStack_a;
  
  uStack_a = (undefined2)((uint)unaff_r6 >> 0x10);
  local_e = 0x43;
  local_10 = (ushort)*(byte *)(param_1 + 0x10);
  local_d = 0;
  local_c = *(undefined2 *)(param_2 + 4);
  (**(code **)(DAT_004b7430 + 0x9c))(&local_10);
  return CONCAT26(uStack_a,CONCAT24(local_c,CONCAT13(local_d,CONCAT12(local_e,local_10))));
}

