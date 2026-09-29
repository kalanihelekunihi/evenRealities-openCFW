
undefined8 smpScActJwncCalcF4(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if (*(char *)(param_1 + 0x3a) == '\0') {
    smpLogByteArray(PTR_s_F4_PKb_005e30f8,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc),0x20,
                    param_4,param_2,param_3,param_4);
    smpLogByteArray(PTR_s_F4_PKa_005e30fc,*(undefined4 *)(*(int *)(param_1 + 0x48) + 8),0x20);
    smpLogByteArray(PTR_s_F4_Nb_005e3100,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10,0x10);
    iVar1 = *(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10;
    uVar2 = 0;
    SmpScCalcF4(param_1,param_2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc),
                *(undefined4 *)(*(int *)(param_1 + 0x48) + 8));
  }
  else {
    smpLogByteArray(PTR_s_F4_PKb_005e30f8,*(undefined4 *)(*(int *)(param_1 + 0x48) + 8),0x20,param_4
                    ,param_2,param_3,param_4);
    smpLogByteArray(PTR_s_F4_PKa_005e30fc,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc),0x20);
    smpLogByteArray(PTR_s_F4_Nb_005e3100,*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10,0x10);
    iVar1 = *(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x10;
    uVar2 = 0;
    SmpScCalcF4(param_1,param_2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 8),
                *(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc));
  }
  return CONCAT44(iVar1,uVar2);
}

