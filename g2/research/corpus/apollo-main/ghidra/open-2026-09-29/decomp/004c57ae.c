
undefined8 dmPhyActDefPhySet(int param_1)

{
  undefined4 unaff_r6;
  undefined2 local_10;
  undefined1 local_e;
  undefined1 local_d;
  undefined4 uVar1;
  
  local_e = 0x45;
  local_10 = 0;
  local_d = *(undefined1 *)(param_1 + 4);
  uVar1 = CONCAT31((int3)((uint)unaff_r6 >> 8),local_d);
  (**(code **)(DAT_004c5868 + 0x9c))(&local_10);
  return CONCAT44(uVar1,CONCAT13(local_d,CONCAT12(local_e,local_10)));
}

