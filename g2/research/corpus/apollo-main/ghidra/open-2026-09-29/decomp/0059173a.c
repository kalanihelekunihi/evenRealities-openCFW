
undefined2 SVC_SSRProcess(int param_1,int param_2)

{
  undefined2 uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint *puVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  bool bVar9;
  undefined8 uVar10;
  
  puVar5 = DAT_00591cb0;
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00591ca4,DAT_00591ca0,DAT_00591cb8,99,DAT_00591ca8,param_1,param_2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_00591cac,DAT_00591cac,param_1,param_2);
    }
  }
  else {
    if (((DAT_00591cb0[1] != 0) || (*DAT_00591cb0 != 0)) &&
       ((DAT_00591cc0[1] != 0 || (*DAT_00591cc0 != 0)))) {
      uVar7 = DAT_00591cb0[1] + DAT_00591cc0[1] + (uint)CARRY4(*DAT_00591cb0,*DAT_00591cc0);
      uVar6 = (uint)((uVar7 & 1) != 0) << 0x1f | *DAT_00591cb0 + *DAT_00591cc0 >> 1;
      uVar3 = 0;
      iVar2 = 0;
      for (iVar4 = 0; iVar4 < 10; iVar4 = iVar4 + 1) {
        puVar5 = (uint *)(DAT_00591d04 + iVar4 * 8);
        uVar8 = *puVar5;
        bVar9 = CARRY4(uVar3,uVar8);
        uVar3 = uVar3 + uVar8;
        iVar2 = iVar2 + puVar5[1] + (uint)bVar9;
      }
      uVar10 = FUN_0047cc60(uVar3,iVar2,10,0);
      uVar1 = FUN_0047cc60(uVar6 + 1,((uVar7 >> 1) + 1) - (uint)(uVar6 != 0xffffffff),
                           (int)uVar10 + 1,
                           ((int)((ulonglong)uVar10 >> 0x20) + 1) - (uint)((int)uVar10 != -1));
      return uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00591ca4,DAT_00591ca0,DAT_00591cb8,0x69,DAT_00591cb4,*puVar5,puVar5[1],
                   *DAT_00591cc0,DAT_00591cc0[1]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_00591cbc,DAT_00591cbc,puVar5[1],*puVar5,puVar5[1],
                          *DAT_00591cc0,DAT_00591cc0[1]);
    }
  }
  return 0;
}

