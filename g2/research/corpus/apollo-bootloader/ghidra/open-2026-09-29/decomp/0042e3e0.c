
undefined8
control_one_wait_42e3e0(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  do {
    iVar1 = bl_runtime_wait(0x800000,1,0xffffffff);
  } while (-1 < iVar1 << 8);
  uVar2 = 299;
  uVar3 = DAT_0042e490;
  elog_output(3,DAT_0042e468,DAT_0042e464,DAT_0042e494,299,DAT_0042e490,param_1,param_4);
  return CONCAT44(uVar3,uVar2);
}

