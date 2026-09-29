
int touch_gesture_state_machine(ushort *param_1,int param_2,undefined4 param_3,int param_4)

{
  uint uVar1;
  uint uVar2;
  undefined1 uVar3;
  byte bVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  
  if (param_1 == (ushort *)0x0) {
    iVar7 = 0;
  }
  else {
    timeout_default_1000_if_zero();
    iVar7 = (int)param_1 + 0x4d;
    memset(iVar7,0,3);
    memcpy(param_1 + 2,param_1 + 6,8);
    *(char *)(param_1 + 6) = (char)param_2;
    *(char *)((int)param_1 + 0xd) = (char)param_3;
    *(int *)(param_1 + 8) = param_4;
    if (param_2 == 1) {
      if ((char)param_1[2] == '\0') {
        memset(param_1 + 0x18,0,0x1c);
        gesture_policy_helper_0bfc(param_1,param_3,param_4);
        *(undefined1 *)(param_1 + 0x26) = 0;
        param_1[0xe] = 0;
        param_1[0xf] = 0;
        memcpy(param_1 + 10,param_1 + 6,8);
        if ((*(char *)((int)param_1 + 0x21) == '\0') ||
           (300 < (uint)(*(int *)(param_1 + 8) - *(int *)(param_1 + 0x12)))) {
          *(undefined1 *)(param_1 + 0x10) = 1;
          logger_stub(DAT_000043f0,*(undefined1 *)((int)param_1 + 0xd),*(undefined4 *)(param_1 + 8),
                      DAT_000043dc);
        }
        else {
          if ((char)param_1[0x10] != -1) {
            *(char *)(param_1 + 0x10) = (char)param_1[0x10] + '\x01';
          }
          logger_stub(DAT_000043ec,(char)param_1[0x10],*(undefined1 *)((int)param_1 + 0xd),
                      *(int *)(param_1 + 8),DAT_000043dc);
        }
        *(undefined4 *)(param_1 + 0x14) = *(undefined4 *)(param_1 + 8);
        *(undefined1 *)(param_1 + 0x16) = *(undefined1 *)((int)param_1 + 0xd);
        *(undefined1 *)((int)param_1 + 0x4d) = 1;
        logger_stub(DAT_000043f4,DAT_000043dc);
      }
      else {
        gesture_policy_helper_0bfc(param_1,param_3,param_4);
        uVar2 = *(int *)(param_1 + 8) - *(int *)(param_1 + 0xc);
        *(uint *)(param_1 + 0xe) = uVar2;
        if ((char)param_1[0x26] == '\0') {
          iVar6 = (uint)*(byte *)((int)param_1 + 0xd) - (uint)*(byte *)((int)param_1 + 0x15);
          uVar1 = iVar6 + (iVar6 >> 0x1f) ^ iVar6 >> 0x1f;
          if ((int)uVar1 < 0x19) {
            if (*param_1 <= uVar2) {
              *(undefined1 *)(param_1 + 0x26) = 2;
              *(undefined1 *)((int)param_1 + 0x21) = 0;
              *(undefined1 *)(param_1 + 0x10) = 0;
              logger_stub(DAT_000043fc,uVar2,DAT_000043dc);
              *(undefined1 *)((int)param_1 + 0x4d) = 0x10;
            }
          }
          else {
            *(undefined1 *)(param_1 + 0x26) = 1;
            *(undefined1 *)((int)param_1 + 0x21) = 0;
            *(undefined1 *)(param_1 + 0x10) = 0;
            if (99 < (uint)(param_4 - *(int *)(param_1 + 0x14))) {
              *(int *)(param_1 + 0x14) = param_4;
              *(byte *)(param_1 + 0x16) = *(byte *)((int)param_1 + 0xd);
              uVar5 = DAT_000043f8;
              if (-1 < iVar6) {
                uVar5 = DAT_000043e4;
              }
              logger_stub(DAT_000043e8,iVar6,uVar5,(char)param_1[0x25],DAT_000043dc);
              if (iVar6 < 0) {
                uVar3 = 0x20;
              }
              else {
                uVar3 = 0x40;
              }
              *(undefined1 *)((int)param_1 + 0x4d) = uVar3;
              *(char *)(param_1 + 0x27) = (char)uVar1;
              *(char *)((int)param_1 + 0x4f) = (char)param_1[0x25];
            }
          }
        }
        else if ((char)param_1[0x26] == '\x01') {
          iVar6 = (uint)*(byte *)((int)param_1 + 0xd) - (uint)(byte)param_1[0x16];
          uVar2 = iVar6 + (iVar6 >> 0x1f) ^ iVar6 >> 0x1f;
          if ((0xe < (int)uVar2) && (99 < (uint)(param_4 - *(int *)(param_1 + 0x14)))) {
            *(int *)(param_1 + 0x14) = param_4;
            *(byte *)(param_1 + 0x16) = *(byte *)((int)param_1 + 0xd);
            uVar5 = DAT_000043f8;
            if (-1 < iVar6) {
              uVar5 = DAT_000043e4;
            }
            logger_stub(DAT_00004400,iVar6,uVar5,(char)param_1[0x25],DAT_000043dc);
            if (iVar6 < 0) {
              uVar3 = 0x20;
            }
            else {
              uVar3 = 0x40;
            }
            *(undefined1 *)((int)param_1 + 0x4d) = uVar3;
            *(char *)(param_1 + 0x27) = (char)uVar2;
            *(char *)((int)param_1 + 0x4f) = (char)param_1[0x25];
          }
        }
      }
    }
    else if (param_2 == 0) {
      if ((char)param_1[2] == '\0') {
        if (((byte)((char)param_1[0x10] - 5U) < 5) &&
           (300 < (uint)(param_4 - *(int *)(param_1 + 0x12)))) {
          logger_stub(DAT_00004404,DAT_000043dc);
          *(undefined1 *)(param_1 + 0x10) = 0;
          attention_release_timeout_rearm();
        }
        else if ((*(char *)((int)param_1 + 0x21) != '\0') &&
                (300 < (uint)(param_4 - *(int *)(param_1 + 0x12)))) {
          *(undefined1 *)((int)param_1 + 0x21) = 0;
          logger_stub(DAT_000043e0,(char)param_1[0x10],DAT_000043dc);
          bVar4 = (byte)param_1[0x10];
          if ((bVar4 != 2) && ((bVar4 == 1 || (9 < bVar4)))) {
            *(undefined1 *)((int)param_1 + 0x4d) = 4;
          }
          *(byte *)(param_1 + 0x27) = bVar4;
          *(undefined1 *)(param_1 + 0x10) = 0;
        }
      }
      else {
        *(undefined1 *)((int)param_1 + 0x4d) = 2;
        uVar5 = DAT_000043dc;
        logger_stub(DAT_00004408,DAT_000043dc);
        *(int *)(param_1 + 0xe) = *(int *)(param_1 + 8) - *(int *)(param_1 + 0xc);
        iVar6 = (uint)*(byte *)((int)param_1 + 0xd) - (uint)(byte)param_1[0x16];
        uVar2 = iVar6 + (iVar6 >> 0x1f) ^ iVar6 >> 0x1f;
        logger_stub(DAT_0000440c,(uint)*(byte *)((int)param_1 + 0xd),*(int *)(param_1 + 8),uVar5);
        if ((char)param_1[0x26] == '\x02') {
          *(undefined1 *)(param_1 + 0x26) = 0;
          *(undefined1 *)((int)param_1 + 0x21) = 0;
          *(undefined1 *)(param_1 + 0x10) = 0;
          *(int *)(param_1 + 0x12) = param_4;
          logger_stub(DAT_00004410,DAT_000043dc);
        }
        else if ((char)param_1[0x26] == '\x01') {
          *(undefined1 *)(param_1 + 0x26) = 0;
          *(int *)(param_1 + 0x12) = param_4;
          if (0xe < (int)uVar2) {
            *(int *)(param_1 + 0x14) = param_4;
            *(undefined1 *)(param_1 + 0x16) = *(undefined1 *)((int)param_1 + 0xd);
            uVar5 = DAT_000043f8;
            if (-1 < iVar6) {
              uVar5 = DAT_000043e4;
            }
            logger_stub(DAT_00004414,iVar6,uVar5,(char)param_1[0x25],DAT_000043dc);
            if (iVar6 < 0) {
              bVar4 = 0x20;
            }
            else {
              bVar4 = 0x40;
            }
            *(byte *)((int)param_1 + 0x4d) = *(byte *)((int)param_1 + 0x4d) | bVar4;
            *(char *)(param_1 + 0x27) = (char)uVar2;
            *(char *)((int)param_1 + 0x4f) = (char)param_1[0x25];
          }
        }
        else if (*(uint *)(param_1 + 0xe) < 300) {
          *(undefined1 *)((int)param_1 + 0x21) = 1;
          *(int *)(param_1 + 0x12) = param_4;
          if ((char)param_1[0x10] == '\x02') {
            *(byte *)((int)param_1 + 0x4d) = *(byte *)((int)param_1 + 0x4d) | 8;
            *(undefined1 *)(param_1 + 0x27) = 2;
          }
          else {
            logger_stub(DAT_00004418,DAT_000043dc);
          }
        }
        else {
          *(int *)(param_1 + 0x12) = param_4;
        }
      }
    }
  }
  return iVar7;
}

