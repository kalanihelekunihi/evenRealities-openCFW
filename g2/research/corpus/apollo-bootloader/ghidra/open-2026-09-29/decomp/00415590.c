
undefined8 redirect_init(void)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 in_r3;
  undefined4 uVar5;
  
  piVar1 = DAT_004155ec;
  iVar3 = bl_runtime_flags_create(0);
  *piVar1 = iVar3;
  piVar2 = DAT_004155f0;
  iVar3 = bl_runtime_flags_create(0);
  *piVar2 = iVar3;
  if ((*piVar1 == 0) || (*piVar2 == 0)) {
    uVar5 = 0x271;
    elog_output(1,DAT_00415604,DAT_00415600,DAT_004155fc,0x271,DAT_004155f8,in_r3);
    uVar4 = 0xffffffff;
  }
  else {
    uVar5 = 0x275;
    elog_output(3,DAT_00415604,DAT_00415600,DAT_004155fc,0x275,DAT_00415608,in_r3);
    uVar4 = 0;
  }
  return CONCAT44(uVar5,uVar4);
}

