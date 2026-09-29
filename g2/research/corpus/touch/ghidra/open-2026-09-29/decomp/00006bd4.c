
uint touch_sub_38d4(uint param_1,uint param_2,int *param_3)

{
  undefined2 uVar1;
  int iVar2;
  uint uVar3;
  uint *puVar4;
  uint uVar5;
  
  if (param_3 == (int *)0x0) {
    uVar5 = 1;
  }
  else if (param_2 == 0) {
    uVar5 = 1;
  }
  else if (param_1 < 5) {
    uVar3 = (param_2 + param_1) - 1;
    if (uVar3 < 5) {
      iVar2 = touch_state_298e_status80(param_3);
      if (iVar2 == 0x80) {
        uVar5 = 0x40;
      }
      else {
        touch_sub_2e40(param_3);
        iVar2 = param_3[2];
        puVar4 = (uint *)**(undefined4 **)(*param_3 + 8);
        *(undefined1 *)(iVar2 + 0x73) = 0;
        uVar1 = (undefined2)param_1;
        if ((((*(char *)(iVar2 + 0x55) == '\x02') || (*(char *)(iVar2 + 0x55) == '\x04')) &&
            (*(ushort *)(iVar2 + 0x48) == param_1)) &&
           ((*(ushort *)(iVar2 + 0x46) == param_2 && (param_2 < 0x16)))) {
          uVar5 = *(uint *)(param_3[1] + 8);
          if (((uVar5 & 0x2000) == 0) && (*(int *)(param_3[1] + 8) << 0x1b < 0)) {
            *(undefined1 *)(iVar2 + 0x73) = 1;
            *(undefined2 *)(iVar2 + 0x34) = uVar1;
            if (*(code **)param_3[2] != (code *)0x0) {
              (**(code **)param_3[2])(param_3[7]);
            }
            *puVar4 = *puVar4 & 0x7fffffff;
            *puVar4 = *puVar4 | 0x80000000;
            puVar4[0x50] = 1;
            return uVar5 & 0x2000;
          }
        }
        uVar5 = event_dispatcher(2,param_3);
        if (uVar5 == 0) {
          *(uint *)(param_3[1] + 8) = *(uint *)(param_3[1] + 8) & 0xffffffcf;
          *(uint *)(param_3[1] + 8) = *(uint *)(param_3[1] + 8) | 0x10;
          *(undefined1 *)(iVar2 + 0x71) = 3;
          *puVar4 = *puVar4 | 0x30000;
          *puVar4 = *puVar4 & DAT_00006d6c;
          puVar4[0x1c] = puVar4[0x1c] & DAT_00006d70;
          puVar4[0x1c] = puVar4[0x1c] | 0x10000;
          *(uint *)(**(int **)(*param_3 + 8) + 0x70) =
               *(uint *)(**(int **)(*param_3 + 8) + 0x70) & 0xffff0000;
          *(uint *)(**(int **)(*param_3 + 8) + 0x70) =
               *(uint *)(**(int **)(*param_3 + 8) + 0x70) | *(uint *)(param_3[2] + 0x20);
          puVar4[0x1d] = *(byte *)(iVar2 + 0x76) | 0x80000000;
          puVar4[0x4a] = 0x10000;
          *(undefined2 *)(iVar2 + 0x48) = uVar1;
          *(undefined2 *)(iVar2 + 0x34) = uVar1;
          *(short *)(iVar2 + 0x36) = (short)uVar3;
          *(undefined1 *)(iVar2 + 0x61) = 1;
          if (param_2 < 0x16) {
            *(undefined1 *)(iVar2 + 0x73) = 1;
          }
          touch_sub_334c(param_1,param_2,param_3);
        }
      }
    }
    else {
      uVar5 = 1;
    }
  }
  else {
    uVar5 = 1;
  }
  return uVar5;
}

