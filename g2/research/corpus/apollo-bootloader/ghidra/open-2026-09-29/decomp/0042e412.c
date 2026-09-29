
undefined8
control_two_publish_42e412(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar1 = 0x139;
  uVar2 = DAT_0042e498;
  elog_output(3,DAT_0042e468,DAT_0042e464,DAT_0042e49c,0x139,DAT_0042e498,param_1,param_4);
  bl_runtime_flags_set(*(undefined4 *)(DAT_0042e46c + 0x1c),1 << (uint)param_1);
  return CONCAT44(uVar2,uVar1);
}

