
undefined8 dmPhyActPhyUpdate(int param_1,int param_2)

{
  undefined4 unaff_r6;
  ushort local_10;
  undefined1 local_e;
  undefined1 local_d;
  undefined1 local_c;
  undefined1 uStack_b;
  undefined2 local_a;
  
  uStack_b = (undefined1)((uint)unaff_r6 >> 8);
  local_e = 0x46;
  local_10 = (ushort)*(byte *)(param_1 + 0x10);
  local_d = *(undefined1 *)(param_2 + 4);
  local_a = *(undefined2 *)(param_1 + 0xc);
  local_c = local_d;
  (**(code **)(DAT_004c5868 + 0x9c))(&local_10);
  return CONCAT26(local_a,CONCAT15(uStack_b,CONCAT14(local_c,CONCAT13(local_d,CONCAT12(local_e,
                                                  local_10)))));
}

