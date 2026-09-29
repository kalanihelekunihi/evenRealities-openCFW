
undefined8
service_even_ai_fn_00497ea2(byte param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined1 *puVar2;
  byte *pbVar3;
  undefined4 uVar4;
  undefined2 uVar5;
  
  even_ai_heartbeat_timer_mgr_start(10000);
  if (param_1 == 1) {
    bVar1 = *param_2;
    if (bVar1 != 1) {
      if (bVar1 == 0) {
LAB_00497f26:
        uVar4 = 0xffffffff;
        goto LAB_00497ef4;
      }
      if (bVar1 == 3) {
        FUN_004e1fa6();
        puVar2 = DAT_004985a8;
        DAT_004985a8[1] = 1;
        puVar2[2] = *param_2;
        FUN_004e1fbe();
      }
      else {
        if (2 < bVar1) goto LAB_00497f26;
        FUN_004e1fa6();
        puVar2 = DAT_004985a8;
        *DAT_004985a8 = 1;
        puVar2[1] = 1;
        puVar2[2] = *param_2;
        FUN_004e1fbe();
      }
    }
  }
  else {
    if (param_1 == 0) {
LAB_0049808c:
      uVar4 = 0xffffffff;
      goto LAB_00497ef4;
    }
    if (param_1 == 3) {
      FUN_004e1fa6();
      puVar2 = DAT_004985a8;
      DAT_004985a8[1] = 3;
      puVar2[0x10] = param_2[1];
      puVar2[0x11] = param_2[2];
      if (*(ushort *)(param_2 + 4) < 0x201) {
        uVar5 = *(undefined2 *)(param_2 + 4);
      }
      else {
        uVar5 = 0x200;
      }
      *(undefined2 *)(puVar2 + 0x16) = uVar5;
      FUN_00439be4(puVar2 + 0x18,param_2 + 6,*(undefined2 *)(puVar2 + 0x16));
      FUN_004e1fbe();
    }
    else if (param_1 < 3) {
      FUN_004e1fa6();
      puVar2 = DAT_004985a8;
      DAT_004985a8[1] = 2;
      FUN_004e1fbe();
      if (2 < *param_2 - 1) {
        uVar4 = 0xffffffff;
        goto LAB_00497ef4;
      }
      FUN_004e1fa6();
      puVar2[8] = *param_2;
      FUN_004e1fbe();
    }
    else if (param_1 == 5) {
      FUN_004e1fa6();
      puVar2 = DAT_004985a8;
      DAT_004985a8[1] = 5;
      puVar2[0x10] = param_2[1];
      puVar2[0x11] = param_2[2];
      puVar2[0x12] = param_2[0x207];
      if (*(ushort *)(param_2 + 4) < 0x201) {
        uVar5 = *(undefined2 *)(param_2 + 4);
      }
      else {
        uVar5 = 0x200;
      }
      *(undefined2 *)(puVar2 + 0x16) = uVar5;
      FUN_00439be4(puVar2 + 0x18,param_2 + 6,*(undefined2 *)(puVar2 + 0x16));
      FUN_004e1fbe();
    }
    else if (param_1 < 5) {
      FUN_004e1fa6();
      DAT_004985a8[1] = 4;
      FUN_004e1fbe();
    }
    else if (param_1 == 7) {
      FUN_004e1fa6();
      puVar2 = DAT_004985a8;
      DAT_004985a8[1] = 7;
      puVar2[2] = *param_2;
      FUN_004e1fbe();
    }
    else if (param_1 < 7) {
      FUN_004e1fa6();
      puVar2 = DAT_004985a8;
      DAT_004985a8[1] = 6;
      puVar2[2] = param_2[1];
      *(undefined4 *)(puVar2 + 0xc) = *(undefined4 *)(param_2 + 4);
      puVar2[0x12] = param_2[0x10b];
      if (*(ushort *)(param_2 + 8) < 0x201) {
        uVar5 = *(undefined2 *)(param_2 + 8);
      }
      else {
        uVar5 = 0x200;
      }
      *(undefined2 *)(puVar2 + 0x16) = uVar5;
      FUN_00439be4(puVar2 + 0x18,param_2 + 10,*(undefined2 *)(puVar2 + 0x16));
      FUN_004e1fbe();
    }
    else if (param_1 == 9) {
      FUN_004e1fa6();
      DAT_004985a8[1] = 9;
      FUN_004e1fbe();
    }
    else if (param_1 < 9) {
      FUN_004e1fa6();
      puVar2 = DAT_004985a8;
      DAT_004985a8[1] = 8;
      puVar2[2] = *param_2;
      FUN_004e1fbe();
    }
    else {
      if (param_1 != 10) goto LAB_0049808c;
      FUN_004e1fa6();
      DAT_004985a8[1] = 10;
      pbVar3 = DAT_004985cc;
      *DAT_004985cc = *param_2;
      pbVar3[1] = param_2[1];
      pbVar3[2] = param_2[3];
      FUN_004e1fbe();
    }
  }
  uVar4 = 0;
LAB_00497ef4:
  return CONCAT44(param_4,uVar4);
}

