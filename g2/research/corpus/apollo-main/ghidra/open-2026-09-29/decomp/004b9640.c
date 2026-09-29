
char TPL_SendPacket(undefined1 param_1,byte param_2,char param_3,undefined4 param_4,int param_5,
                   uint param_6)

{
  int *piVar1;
  undefined4 uVar2;
  undefined1 uVar3;
  char cVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  uint uVar9;
  byte bVar10;
  uint uVar11;
  uint uVar12;
  undefined2 uVar13;
  uint uVar14;
  undefined4 local_38;
  undefined4 local_34;
  undefined2 local_30 [2];
  int local_2c;
  undefined4 uStack_28;
  
  if ((param_5 == 0) || ((param_6 & 0xffff) == 0)) {
    cVar4 = '\v';
  }
  else {
    uStack_28 = param_4;
    if ((param_6 & 0xffff) < 0x1001) {
      sVar5 = slave_cmd_pipe_get_0046f2c6();
      piVar1 = DAT_004b9a54;
      uVar11 = (uint)(ushort)(sVar5 - 0xb);
      if (*DAT_004b9a54 == 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a4c,0x22a,DAT_004b9a58);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004b9a5c,DAT_004b9a5c);
        }
        cVar4 = '\x04';
      }
      else {
        iVar7 = osMutexAcquire(*DAT_004b9a54,100);
        iVar6 = DAT_004b9a6c;
        if (iVar7 == 0) {
          local_2c = DAT_004b9a68;
          FUN_0043c0e4(DAT_004b9a68,0x1000,0);
          FUN_0043c0e4(iVar6,0x101,0);
          FUN_00439be4(local_2c,param_5,param_6 & 0xffff);
          local_30[0] = FUN_0049acd4(local_2c,param_6 & 0xffff,0);
          uVar13 = (undefined2)uVar11;
          uVar11 = (int)((uVar11 & 0xffff) + (param_6 & 0xffff) + -1) / (int)(uVar11 & 0xffff);
          uVar8 = *DAT_004b9a70;
          local_34 = DAT_004b9a70[1];
          local_38._1_1_ = (byte)((uint)uVar8 >> 8);
          local_38._2_2_ = (undefined2)((uint)uVar8 >> 0x10);
          local_38._0_2_ = CONCAT11(local_38._1_1_ & 0xf | param_3 << 4,(char)uVar8);
          uVar3 = osKernelGetTickCount();
          uVar8 = local_34;
          local_38._0_3_ = CONCAT12(uVar3,(undefined2)local_38);
          local_34 = CONCAT31(local_34._1_3_,(char)uVar11);
          uVar2 = local_34;
          local_34._3_1_ = SUB41(uVar8,3);
          local_34._0_2_ = (undefined2)uVar2;
          local_34 = CONCAT13(local_34._3_1_ & 0xfe | param_2 & 1,
                              CONCAT12((char)param_4,(undefined2)local_34));
          uVar14 = (uint)CONCAT12(param_1,uVar13);
          for (bVar10 = 1; (uint)bVar10 <= (uVar11 & 0xffff); bVar10 = bVar10 + 1) {
            uVar12 = (int)(short)(bVar10 - 1) * (int)(short)uVar14;
            if ((uint)bVar10 == (uVar11 & 0xffff)) {
              uVar9 = param_6 - uVar12;
            }
            else {
              uVar9 = uVar14 & 0xffff;
            }
            cVar4 = (char)uVar9;
            if ((uint)bVar10 == (uVar11 & 0xffff)) {
              cVar4 = cVar4 + '\x02';
            }
            local_38 = CONCAT13(cVar4,(undefined3)local_38);
            local_34._0_2_ = CONCAT11(bVar10,(undefined1)local_34);
            FUN_00439be4(iVar6,&local_38,8);
            FUN_00439be4(iVar6 + 8,local_2c + (uVar12 & 0xffff),uVar9 & 0xffff);
            if ((uint)bVar10 == (uVar11 & 0xffff)) {
              FUN_00439be4(iVar6 + (uVar9 & 0xffff) + 8,local_30,2);
            }
            cVar4 = '\0';
            if ((char)(uVar14 >> 0x10) == '\0') {
              if (*(int *)(DAT_004b9a30 + 0xc) != 0) {
                cVar4 = (**(code **)(DAT_004b9a30 + 0xc))(iVar6,local_38._3_1_ + 8);
              }
            }
            else {
              iVar7 = FUN_0043d0ce();
              if (iVar7 << 0x1e < 0) {
                FUN_0043d574(1,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a4c,0x293,DAT_004b9a74,
                             local_38 >> 8 & 0xf);
              }
              iVar7 = FUN_0043d0ce();
              if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                compress_log_output(0x4400000,DAT_004b9a78,DAT_004b9a78,local_38._1_1_ & 0xf);
              }
            }
            if (cVar4 != '\0') {
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                FUN_0043d574(1,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a4c,0x298,DAT_004b99fc,cVar4);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x4400000,DAT_004b9a00,DAT_004b9a00,cVar4);
              }
              osMutexRelease(*piVar1);
              return cVar4;
            }
          }
          osMutexRelease(*piVar1);
          cVar4 = '\0';
        }
        else {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a4c,0x230,DAT_004b9a60);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004b9a64,DAT_004b9a64);
          }
          cVar4 = '\x04';
        }
      }
    }
    else {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004b9a10,DAT_004b9a0c,DAT_004b9a4c,0x221,DAT_004b9a48,param_6 & 0xffff,
                     0x1000);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_004b9a50,DAT_004b9a50,param_6 & 0xffff,0x1000);
      }
      cVar4 = '\v';
    }
  }
  return cVar4;
}

