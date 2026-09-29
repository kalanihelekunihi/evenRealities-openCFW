
undefined4 smpiScActJwncSetup(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined *puVar1;
  
  FUN_0053634e(*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14),0x10);
  smpLogByteArray(PTR_s_Rand_Na_005e38ac,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x14),0x10);
  puVar1 = PTR_DAT_005e38b0;
  FUN_00542a44(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x20,PTR_DAT_005e38b0);
  FUN_00542a44(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x30,puVar1);
  *(undefined1 *)(param_1 + 0x3f) = 3;
  return param_4;
}

