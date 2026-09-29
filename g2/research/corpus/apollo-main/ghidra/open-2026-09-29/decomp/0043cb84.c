
void compress_log_encode_record(uint param_1,byte *param_2,double *param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  bool bVar5;
  int *piVar6;
  byte *pbVar7;
  byte *pbVar8;
  ushort uVar9;
  uint uVar10;
  short sVar11;
  byte bVar12;
  uint local_54;
  undefined4 local_50;
  uint local_4c;
  float local_48 [8];
  undefined4 uStack_28;
  
  uStack_28 = param_4;
  FUN_0043c0e4(&local_54,0x2c,0);
  uVar10 = param_1 >> 0x1a & 7;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1d < 0) {
    if (5 < uVar10) {
      return;
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) && (uVar3 = FUN_0043d0da(), uVar3 < uVar10)) {
      return;
    }
  }
  bVar12 = *DAT_0043d108;
  *DAT_0043d108 = *DAT_0043d108 + 1;
  local_54 = local_54 & 0xffff0000 | 0x7b | (uint)bVar12 << 8;
  uVar10 = osKernelGetTickCount();
  local_54 = local_54 & 0xffff | uVar10 % 1000 << 0x10 | 0xdc000000;
  local_50 = service_time_current_epoch_get();
  sVar11 = 0xc;
  uVar9 = 0;
  bVar12 = 0;
  local_4c = param_1;
  do {
    do {
      while( true ) {
        if (((*param_2 == 0) || (0x1f < uVar9)) || (((byte)(param_1 >> 0x16) & 0xf) <= bVar12)) {
          local_4c = param_1 & 0xfc3fffff | (uint)bVar12 << 0x16;
          compress_log_ring_write(&local_54,sVar11);
          return;
        }
        if (*param_2 == 0x25) break;
        param_2 = param_2 + 1;
      }
      pbVar7 = param_2 + 1;
      bVar5 = false;
      if (((*pbVar7 == 0x30) || (*pbVar7 == 0x2d)) ||
         ((*pbVar7 == 0x2b || ((*pbVar7 == 0x20 || (*pbVar7 == 0x23)))))) {
        pbVar7 = param_2 + 2;
      }
      for (; *pbVar7 - 0x30 < 10; pbVar7 = pbVar7 + 1) {
      }
      pbVar8 = pbVar7;
      if (*pbVar7 == 0x2e) {
        pbVar8 = pbVar7 + 1;
        if (*pbVar8 == 0x2a) {
          param_3 = (double *)((int)param_3 + 4);
          pbVar8 = pbVar7 + 2;
        }
        else {
          for (; *pbVar8 - 0x30 < 10; pbVar8 = pbVar8 + 1) {
          }
        }
      }
      if (*pbVar8 == 0x6c) {
        param_2 = pbVar8 + 1;
        if (pbVar8[1] == 0x6c) {
          bVar5 = true;
          param_2 = pbVar8 + 2;
        }
      }
      else {
        param_2 = pbVar8;
        if ((*pbVar8 == 0x68) && (param_2 = pbVar8 + 1, *param_2 == 0x68)) {
          param_2 = pbVar8 + 2;
        }
      }
    } while (*param_2 == 0);
    bVar1 = *param_2;
    if (bVar1 == 0x25) goto LAB_0043ce7c;
    if (bVar1 == 0x46) {
LAB_0043ce00:
      if (uVar9 + 4 < 0x21) {
        param_3 = (double *)((int)param_3 + 7U & 0xfffffff8);
        *(float *)((int)local_48 + (uint)uVar9) = (float)*param_3;
        uVar9 = uVar9 + 4;
        sVar11 = sVar11 + 4;
      }
      else {
        param_3 = (double *)((int)param_3 + 7U & 0xfffffff8);
      }
      bVar12 = bVar12 + 1;
      param_3 = param_3 + 1;
    }
    else if (((bVar1 == 0x58) || (bVar1 == 99)) || (bVar1 == 100)) {
LAB_0043cd9e:
      if (uVar9 + 4 < 0x21) {
        if (bVar5) {
          piVar6 = (int *)((int)param_3 + 7U & 0xfffffff8);
          iVar2 = *piVar6;
          param_3 = (double *)(piVar6 + 2);
        }
        else {
          iVar2 = *(int *)param_3;
          param_3 = (double *)((int)param_3 + 4);
        }
        *(int *)((int)local_48 + (uint)uVar9) = iVar2;
        uVar9 = uVar9 + 4;
        sVar11 = sVar11 + 4;
      }
      else if (bVar5) {
        param_3 = (double *)(((int)param_3 + 7U & 0xfffffff8) + 8);
      }
      else {
        param_3 = (double *)((int)param_3 + 4);
      }
      bVar12 = bVar12 + 1;
    }
    else {
      if (bVar1 == 0x66) goto LAB_0043ce00;
      if (((bVar1 == 0x69) || (bVar1 == 0x6f)) || (bVar1 == 0x70)) goto LAB_0043cd9e;
      if (bVar1 == 0x73) {
        if (uVar9 + 0x10 < 0x21) {
          iVar2 = *(int *)param_3;
          if (iVar2 == 0) {
            uVar10 = 0;
          }
          else {
            uVar10 = FUN_0044a43c(iVar2);
          }
          if (uVar10 < 0x10) {
            iVar4 = 0;
          }
          else {
            iVar4 = uVar10 - 0x10;
            uVar10 = 0x10;
          }
          if ((iVar2 != 0) && (uVar10 != 0)) {
            FUN_00439be4((int)local_48 + (uint)uVar9,iVar2 + iVar4,uVar10);
          }
          if (uVar10 < 0x10) {
            FUN_0043c0e4((int)local_48 + uVar10 + uVar9,0x10 - uVar10,0);
          }
          uVar9 = uVar9 + 0x10;
          sVar11 = sVar11 + 0x10;
        }
        bVar12 = bVar12 + 1;
        param_3 = (double *)((int)param_3 + 4);
      }
      else {
        if ((bVar1 == 0x75) || (bVar1 == 0x78)) goto LAB_0043cd9e;
        if (uVar9 + 4 < 0x21) {
          iVar2 = *(int *)param_3;
          param_3 = (double *)((int)param_3 + 4);
          *(int *)((int)local_48 + (uint)uVar9) = iVar2;
          uVar9 = uVar9 + 4;
          sVar11 = sVar11 + 4;
          bVar12 = bVar12 + 1;
        }
        else {
          param_3 = (double *)((int)param_3 + 4);
          bVar12 = bVar12 + 1;
        }
      }
    }
LAB_0043ce7c:
    param_2 = param_2 + 1;
  } while( true );
}

