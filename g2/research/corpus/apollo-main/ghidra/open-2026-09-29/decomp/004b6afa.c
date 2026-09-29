
undefined8 dmConn2ActWriteAuthToCmpl(int param_1,int param_2)

{
  undefined4 unaff_r6;
  ushort local_10;
  undefined1 local_e;
  undefined1 local_d;
  undefined1 local_c;
  undefined1 uStack_b;
  undefined2 local_a;
  
  uStack_b = (undefined1)((uint)unaff_r6 >> 8);
  local_e = 0x42;
  local_10 = (ushort)*(byte *)(param_1 + 0x10);
  local_d = 0;
  local_a = *(undefined2 *)(param_2 + 6);
  local_c = *(undefined1 *)(param_2 + 4);
  (**(code **)(DAT_004b7430 + 0x9c))(&local_10);
  return CONCAT26(local_a,CONCAT15(uStack_b,CONCAT14(local_c,CONCAT13(local_d,CONCAT12(local_e,
                                                  local_10)))));
}

