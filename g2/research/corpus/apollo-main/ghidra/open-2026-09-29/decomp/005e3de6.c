
void smprScActJwncSetup(int param_1,undefined4 param_2)

{
  undefined *puVar1;
  
  FUN_0053634e(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10,0x10);
  smpLogByteArray(PTR_s_Rand_Nb_005e4214,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10,0x10);
  puVar1 = PTR_DAT_005e4210;
  FUN_00542a44(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x20,PTR_DAT_005e4210);
  FUN_00542a44(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x30,puVar1);
  *(undefined1 *)(param_1 + 0x3f) = 4;
  smpScActJwncCalcF4(param_1,param_2);
  return;
}

