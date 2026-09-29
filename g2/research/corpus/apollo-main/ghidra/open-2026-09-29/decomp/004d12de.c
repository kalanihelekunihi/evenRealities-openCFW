
/* WARNING: Removing unreachable block (ram,0x004d1304) */
/* WARNING: Removing unreachable block (ram,0x004d130c) */
/* WARNING: Removing unreachable block (ram,0x004d1320) */
/* WARNING: Removing unreachable block (ram,0x004d1328) */
/* WARNING: Removing unreachable block (ram,0x004d1330) */
/* WARNING: Removing unreachable block (ram,0x004d133c) */

char FUN_004d12de(byte param_1,char param_2,undefined1 param_3,int param_4,ushort param_5)

{
  int *piVar1;
  int *piVar2;
  undefined4 uVar3;
  undefined1 uVar4;
  char cVar5;
  short sVar6;
  undefined4 uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  byte bVar11;
  uint uVar12;
  ushort uVar13;
  uint uVar14;
  undefined1 local_34;
  byte bStack_33;
  undefined2 uStack_32;
  undefined4 local_30;
  undefined2 local_2c [2];
  int iStack_28;
  
  if ((param_4 == 0) || (param_5 == 0)) {
    cVar5 = '\v';
  }
  else {
    iStack_28 = param_4;
    sVar6 = slave_cmd_pipe_get_0046f2c6();
    piVar1 = DAT_004d15d4;
    uVar14 = (uint)(ushort)(sVar6 - 0xb);
    iVar9 = *DAT_004d15d4;
    if (iVar9 == 0) {
      cVar5 = '\x04';
    }
    else {
      FUN_0043c0e4(iVar9,0x1020,0);
      FUN_00439be4(iVar9,param_4,param_5);
      piVar2 = DAT_004d15d8;
      iVar10 = *DAT_004d15d8;
      if (iVar10 == 0) {
        cVar5 = '\x04';
      }
      else {
        FUN_0043c0e4(iVar10,0xf7,0);
        local_2c[0] = FUN_0049acd4(iVar9,param_5,0);
        uVar12 = ((uVar14 & 0xffff) + (uint)param_5 + 1) / (uVar14 & 0xffff);
        uVar7 = *DAT_004d15dc;
        local_30 = DAT_004d15dc[1];
        bStack_33 = (byte)((uint)uVar7 >> 8);
        uStack_32 = (undefined2)((uint)uVar7 >> 0x10);
        _local_34 = CONCAT11(bStack_33 & 0xf | param_2 << 4,(char)uVar7);
        uVar4 = osKernelGetTickCount();
        uVar7 = local_30;
        _local_34 = CONCAT12(uVar4,_local_34);
        local_30 = CONCAT31(local_30._1_3_,(char)uVar12);
        uVar3 = local_30;
        local_30._3_1_ = SUB41(uVar7,3);
        local_30._0_2_ = (undefined2)uVar3;
        local_30 = CONCAT13(local_30._3_1_ & 0xfe | param_1 & 1,
                            CONCAT12(param_3,(undefined2)local_30));
        for (bVar11 = 1; (uint)bVar11 <= (uVar12 & 0xffff); bVar11 = bVar11 + 1) {
          uVar13 = (ushort)uVar14;
          sVar6 = (bVar11 - 1) * uVar13;
          uVar14 = CONCAT22(sVar6,uVar13);
          if ((uint)bVar11 == (uVar12 & 0xffff)) {
            uVar13 = param_5 - sVar6;
          }
          cVar5 = (char)uVar13;
          if ((uint)bVar11 == (uVar12 & 0xffff)) {
            cVar5 = cVar5 + '\x02';
          }
          _local_34 = CONCAT13(cVar5,_local_34);
          local_30._0_2_ = CONCAT11(bVar11,(undefined1)local_30);
          FUN_00439be4(iVar10,&local_34,8);
          FUN_00439be4(iVar10 + 8,iVar9 + (uVar14 >> 0x10),uVar13);
          if ((uint)bVar11 == (uVar12 & 0xffff)) {
            FUN_00439be4(iVar10 + (uint)uVar13 + 8,local_2c,2);
          }
          cVar5 = '\0';
          if (*(int *)(DAT_004d1578 + 4) != 0) {
            cVar5 = (**(code **)(DAT_004d1578 + 4))(iVar10,uStack_32._1_1_ + 8);
          }
          if (cVar5 != '\0') {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              FUN_0043d574(1,DAT_004d1554,DAT_004d1550,DAT_004d15cc,0x13e,DAT_004d15e0,cVar5);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_004d15e4,DAT_004d15e4,cVar5);
            }
            if (iVar9 != *piVar1) {
              file_heap_free(iVar9);
            }
            if (iVar10 == *piVar2) {
              return cVar5;
            }
            file_heap_free(iVar10);
            return cVar5;
          }
        }
        if (iVar9 != *piVar1) {
          file_heap_free(iVar9);
        }
        if (iVar10 != *piVar2) {
          file_heap_free(iVar10);
        }
        cVar5 = '\0';
      }
    }
  }
  return cVar5;
}

