
undefined8 hciEvtProcessMsg(char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  char cVar2;
  int iVar3;
  undefined2 *puVar4;
  code *pcVar5;
  char *pcVar6;
  byte bVar7;
  undefined4 local_20;
  undefined4 local_1c;
  
  iVar3 = DAT_0056b7c8;
  bVar7 = 0;
  pcVar5 = *(code **)(DAT_0056b7c8 + 8);
  cVar1 = *param_1;
  cVar2 = param_1[1];
  pcVar6 = param_1 + 2;
  local_20 = param_3;
  local_1c = param_4;
  if (cVar1 == '\x05') {
    *DAT_0056b7d4 = *DAT_0056b7d4 + 1;
    iVar3 = hciCoreCisByHandle((uint)(byte)param_1[4] * 0x100 + (uint)(byte)param_1[3]);
    if (iVar3 == 0) {
      bVar7 = 3;
    }
    else {
      bVar7 = 0x46;
    }
  }
  else if (cVar1 == '\b') {
    DAT_0056b7d4[1] = DAT_0056b7d4[1] + 1;
    bVar7 = 0xf;
  }
  else if (cVar1 == '\f') {
    DAT_0056b7d4[2] = DAT_0056b7d4[2] + 1;
    bVar7 = 10;
  }
  else if (cVar1 == '\x0e') {
    DAT_0056b7d4[3] = DAT_0056b7d4[3] + 1;
    hciEvtProcessCmdCmpl(pcVar6,cVar2);
  }
  else if (cVar1 == '\x0f') {
    DAT_0056b7d4[4] = DAT_0056b7d4[4] + 1;
    hciEvtProcessCmdStatus(pcVar6);
  }
  else if (cVar1 == '\x10') {
    DAT_0056b7d4[5] = DAT_0056b7d4[5] + 1;
    bVar7 = 0x14;
  }
  else if (cVar1 == '\x13') {
    hciCoreNumCmplPkts(pcVar6);
    DAT_0056b7d4[6] = DAT_0056b7d4[6] + 1;
  }
  else if (cVar1 == '\x1a') {
    DAT_0056b7d4[7] = DAT_0056b7d4[7] + 1;
  }
  else if (cVar1 == '0') {
    DAT_0056b7d4[8] = DAT_0056b7d4[8] + 1;
    bVar7 = 0xe;
  }
  else if (cVar1 == '>') {
    cVar1 = *pcVar6;
    pcVar6 = param_1 + 3;
    DAT_0056b7d4[9] = DAT_0056b7d4[9] + 1;
    if (cVar1 == '\x01') {
      if (*pcVar6 == '\0') {
        hciCoreConnOpen((uint)(byte)param_1[5] * 0x100 + (uint)(byte)param_1[4]);
      }
      bVar7 = 1;
    }
    else if (cVar1 == '\x02') {
      hciEvtProcessLeAdvReport(pcVar6,cVar2);
    }
    else if (cVar1 == '\x03') {
      bVar7 = 4;
    }
    else if (cVar1 == '\x04') {
      bVar7 = 0xb;
    }
    else if (cVar1 == '\x05') {
      bVar7 = 0x10;
    }
    else if (cVar1 == '\x06') {
      bVar7 = 0x23;
    }
    else if (cVar1 == '\a') {
      bVar7 = 0x24;
    }
    else if (cVar1 == '\b') {
      pcVar5 = *(code **)(iVar3 + 0xc);
      bVar7 = 0x25;
    }
    else if (cVar1 == '\t') {
      pcVar5 = *(code **)(iVar3 + 0xc);
      bVar7 = 0x26;
    }
    else if (cVar1 == '\n') {
      if (*pcVar6 == '\0') {
        hciCoreConnOpen((uint)(byte)param_1[5] * 0x100 + (uint)(byte)param_1[4]);
      }
      bVar7 = 2;
    }
    else if (cVar1 == '\v') {
      hciEvtProcessLeDirectAdvReport(pcVar6,cVar2);
    }
    else if (cVar1 == '\f') {
      bVar7 = 0x2b;
    }
    else if (cVar1 == '\r') {
      hciEvtProcessLeExtAdvReport(pcVar6,cVar2);
    }
    else if (cVar1 == '\x0e') {
      bVar7 = 0x30;
    }
    else if (cVar1 == '\x0f') {
      hciEvtProcessLePerAdvReport(pcVar6,cVar2);
    }
    else if (cVar1 == '\x10') {
      bVar7 = 0x32;
    }
    else if (cVar1 == '\x11') {
      bVar7 = 0x2d;
    }
    else if (cVar1 == '\x12') {
      bVar7 = 0x2e;
    }
    else if (cVar1 == '\x13') {
      bVar7 = 0x2f;
    }
    else if (cVar1 == '\x15') {
      hciEvtProcessLeConlessIQReport(pcVar6,cVar2);
    }
    else if (cVar1 == '\x16') {
      hciEvtProcessLeConnIQReport(pcVar6,cVar2);
    }
    else if (cVar1 == '\x17') {
      iVar3 = FUN_004c9c50();
      if ((iVar3 == 0) || (iVar3 = FUN_0044b610(DAT_0056b7d8,&DAT_0056b7bc,3), iVar3 != 0)) {
        iVar3 = FUN_004c9c50();
        if ((iVar3 == 0) || (iVar3 = FUN_0044b610(DAT_0056b7d8,DAT_0056b7e8,4), iVar3 != 0)) {
          iVar3 = FUN_004c9c50();
          if ((iVar3 == 0) || (iVar3 = FUN_0044b610(DAT_0056b7d8,DAT_0056b7d8,4), iVar3 != 0)) {
            iVar3 = FUN_004c9c50();
            if (iVar3 == 0) {
              iVar3 = FUN_004c9c50();
              if ((iVar3 == 0) || (iVar3 = FUN_0044b610(&DAT_0056b7c0,&DAT_0056b7c4,3), iVar3 != 0))
              {
                WsfTrace(DAT_0056b7d8,DAT_0056b7dc);
              }
            }
            else {
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                local_1c = DAT_0056b7dc;
                local_20 = 0xb0f;
                FUN_0043d574(4,&DAT_0056b7c0,DAT_0056b7e4,DAT_0056b7e0);
              }
            }
          }
          else {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              local_1c = DAT_0056b7dc;
              local_20 = 0xb0f;
              FUN_0043d574(3,&DAT_0056b7c0,DAT_0056b7e4,DAT_0056b7e0);
            }
          }
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            local_1c = DAT_0056b7dc;
            local_20 = 0xb0f;
            FUN_0043d574(2,&DAT_0056b7c0,DAT_0056b7e4,DAT_0056b7e0);
          }
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_1c = DAT_0056b7dc;
          local_20 = 0xb0f;
          FUN_0043d574(1,&DAT_0056b7c0,DAT_0056b7e4,DAT_0056b7e0);
        }
      }
    }
    else if (cVar1 == '\x19') {
      if (*pcVar6 == '\0') {
        hciCoreCisOpen((uint)(byte)param_1[5] * 0x100 + (uint)(byte)param_1[4]);
      }
      bVar7 = 0x44;
    }
    else if (cVar1 == '\x1a') {
      bVar7 = 0x45;
    }
    else if (cVar1 == '\x1b') {
      bVar7 = 0x50;
    }
    else if (cVar1 == '\x1c') {
      bVar7 = 0x51;
    }
    else if (cVar1 == '\x1d') {
      bVar7 = 0x52;
    }
    else if (cVar1 == '\x1e') {
      bVar7 = 0x53;
    }
    else if (cVar1 == '\x1f') {
      bVar7 = 0x47;
    }
    else if (cVar1 == '\"') {
      bVar7 = 0x55;
    }
  }
  else if (cVar1 == 'W') {
    DAT_0056b7d4[0xb] = DAT_0056b7d4[0xb] + 1;
    bVar7 = 0x28;
  }
  else if (cVar1 == -1) {
    DAT_0056b7d4[10] = DAT_0056b7d4[10] + 1;
    bVar7 = 0x13;
  }
  if (bVar7 != 0) {
    puVar4 = (undefined2 *)WsfBufAlloc(*(undefined1 *)(DAT_0056b7cc + (uint)bVar7));
    if (puVar4 != (undefined2 *)0x0) {
      *puVar4 = 0;
      *(byte *)(puVar4 + 1) = bVar7;
      *(undefined1 *)((int)puVar4 + 3) = 0;
      (**(code **)(DAT_0056b7d0 + (uint)bVar7 * 4))(puVar4,pcVar6,cVar2);
      (*pcVar5)(puVar4);
      WsfBufFree(puVar4);
    }
    if (bVar7 == 3) {
      hciCoreConnClose((uint)(byte)pcVar6[2] * 0x100 + (uint)(byte)pcVar6[1]);
    }
    else if (bVar7 == 0x46) {
      hciCoreCisClose((uint)(byte)pcVar6[2] * 0x100 + (uint)(byte)pcVar6[1]);
    }
  }
  return CONCAT44(local_1c,local_20);
}

