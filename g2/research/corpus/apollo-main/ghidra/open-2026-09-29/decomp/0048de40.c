
/* WARNING: Removing unreachable block (ram,0x0048de66) */
/* WARNING: Removing unreachable block (ram,0x0048de6e) */
/* WARNING: Removing unreachable block (ram,0x0048de82) */
/* WARNING: Removing unreachable block (ram,0x0048de8a) */
/* WARNING: Removing unreachable block (ram,0x0048de92) */
/* WARNING: Removing unreachable block (ram,0x0048de9e) */

char FUN_0048de40(byte param_1,char param_2,undefined1 param_3,int param_4,ushort param_5)

{
  int *piVar1;
  int *piVar2;
  char cVar3;
  short sVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  byte bVar9;
  uint uVar10;
  ushort uVar11;
  uint uVar12;
  undefined1 local_34;
  byte bStack_33;
  undefined1 uStack_32;
  byte bStack_31;
  undefined1 local_30;
  undefined1 local_2f [2];
  byte local_2d;
  undefined2 local_2c [2];
  int iStack_28;
  
  if ((param_4 == 0) || (param_5 == 0)) {
    cVar3 = '\v';
  }
  else {
    iStack_28 = param_4;
    sVar4 = slave_cmd_pipe_get_0046f2c6();
    piVar1 = DAT_0048e13c;
    uVar12 = (uint)(ushort)(sVar4 - 0xb);
    iVar7 = *DAT_0048e13c;
    if (iVar7 == 0) {
      cVar3 = '\x04';
    }
    else {
      FUN_0043c0e4(iVar7,0x1020,0);
      FUN_00439be4(iVar7,param_4,param_5);
      piVar2 = DAT_0048e140;
      iVar8 = *DAT_0048e140;
      if (iVar8 == 0) {
        cVar3 = '\x04';
      }
      else {
        FUN_0043c0e4(iVar8,0xf7,0);
        local_2c[0] = FUN_0049acd4(iVar7,param_5,0);
        uVar10 = ((uVar12 & 0xffff) + (uint)param_5 + 1) / (uVar12 & 0xffff);
        uVar5 = *DAT_0048e144;
        bStack_33 = (byte)((uint)uVar5 >> 8);
        bVar9 = bStack_33 & 0xf;
        bStack_31 = (byte)((uint)uVar5 >> 0x18);
        _local_34 = CONCAT12(*DAT_0048e0c8,CONCAT11(bVar9 | param_2 << 4,(char)uVar5));
        _local_30 = CONCAT31((int3)((uint)DAT_0048e144[1] >> 8),(char)uVar10);
        uVar5 = _local_30;
        local_2d = (byte)((uint)DAT_0048e144[1] >> 0x18);
        _local_30 = (undefined2)uVar5;
        _local_30 = CONCAT13(local_2d & 0xfe | param_1 & 1,CONCAT12(param_3,_local_30));
        for (bVar9 = 1; (uint)bVar9 <= (uVar10 & 0xffff); bVar9 = bVar9 + 1) {
          uVar11 = (ushort)uVar12;
          sVar4 = (bVar9 - 1) * uVar11;
          uVar12 = CONCAT22(sVar4,uVar11);
          if ((uint)bVar9 == (uVar10 & 0xffff)) {
            uVar11 = param_5 - sVar4;
          }
          cVar3 = (char)uVar11;
          if ((uint)bVar9 == (uVar10 & 0xffff)) {
            cVar3 = cVar3 + '\x02';
          }
          _local_34 = CONCAT13(cVar3,_local_34);
          _local_30 = CONCAT11(bVar9,local_30);
          FUN_00439be4(iVar8,&local_34,8);
          FUN_00439be4(iVar8 + 8,iVar7 + (uVar12 >> 0x10),uVar11);
          if ((uint)bVar9 == (uVar10 & 0xffff)) {
            FUN_00439be4(iVar8 + (uint)uVar11 + 8,local_2c,2);
          }
          cVar3 = '\0';
          if (*(int *)(DAT_0048e0e0 + 4) != 0) {
            cVar3 = (**(code **)(DAT_0048e0e0 + 4))(iVar8,bStack_31 + 8);
          }
          if (cVar3 != '\0') {
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              FUN_0043d574(1,DAT_0048e0b8,DAT_0048e0b4,DAT_0048e134,0x13f,DAT_0048e148,cVar3);
            }
            iVar6 = FUN_0043d0ce();
            if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_0048e14c,DAT_0048e14c,cVar3);
            }
            if (iVar7 != *piVar1) {
              file_heap_free(iVar7);
            }
            if (iVar8 == *piVar2) {
              return cVar3;
            }
            file_heap_free(iVar8);
            return cVar3;
          }
        }
        if (iVar7 != *piVar1) {
          file_heap_free(iVar7);
        }
        if (iVar8 != *piVar2) {
          file_heap_free(iVar8);
        }
        cVar3 = '\0';
      }
    }
  }
  return cVar3;
}

