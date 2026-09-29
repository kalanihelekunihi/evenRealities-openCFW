
int FUN_00420254(undefined4 param_1,int param_2,int *param_3,undefined4 param_4)

{
  byte bVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  undefined1 auStack_30 [4];
  undefined4 local_2c;
  undefined4 local_28;
  uint local_24;
  undefined4 uStack_20;
  
  puVar2 = DAT_00420874;
  local_2c = 0;
  local_28 = 0;
  local_24 = 0;
  iVar4 = 0;
  while ((iVar4 == 0 && (*(char *)(DAT_00420b04 + 0xc) != '\0'))) {
    iVar4 = 1;
  }
  if (iVar4 == 1) {
    iVar3 = -1;
  }
  else {
    uStack_20 = param_4;
    iVar3 = am_hal_mspi_initialize(param_1,DAT_00420874);
    if (iVar3 == 0) {
      iVar3 = am_hal_mspi_power_control(*puVar2,0,0);
      if (iVar3 == 0) {
        local_2c = 0x100;
        local_28 = DAT_00420c20;
        local_24 = local_24 & 0xffffff00;
        iVar3 = am_hal_mspi_configure(*puVar2,&local_2c);
        if (iVar3 == 0) {
          if (param_2 == 0) {
            iVar3 = am_hal_mspi_device_configure(*puVar2,DAT_00420c28);
          }
          else {
            iVar3 = am_hal_mspi_device_configure(*puVar2,param_2);
          }
          if (iVar3 == 0) {
            iVar3 = am_hal_mspi_enable(*puVar2);
            if (iVar3 == 0) {
              FUN_0041ff34(0);
              FUN_0041fadc(param_1,0x10);
              FUN_0041d90e(0x67,auStack_30);
              iVar3 = am_hal_mspi_interrupt_clear(*puVar2,0x1a80);
              if (iVar3 == 0) {
                iVar3 = am_hal_mspi_interrupt_enable(*puVar2,0x1a80);
                if (iVar3 == 0) {
                  FUN_0041fdde(0x15,4);
                  FUN_0041fdc0(0x15);
                  FUN_0041b8e0();
                  iVar3 = DAT_00420b04;
                  *(undefined4 *)(DAT_00420b04 + iVar4 * 0x10) = param_1;
                  if (param_2 == 0) {
                    bVar1 = *(byte *)(DAT_00420c38 + 8);
                  }
                  else {
                    bVar1 = *(byte *)(param_2 + 8);
                  }
                  *(uint *)(iVar4 * 0x10 + iVar3 + 4) = (uint)bVar1;
                  *(undefined4 *)(iVar4 * 0x10 + iVar3 + 8) = *puVar2;
                  *(undefined1 *)(iVar4 * 0x10 + iVar3 + 0xc) = 1;
                  *param_3 = iVar3 + iVar4 * 0x10;
                  elog_output(3,DAT_00420adc,DAT_00420978,DAT_00420c1c,0x27a,DAT_00420c3c);
                  iVar3 = 0;
                }
                else {
                  elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420c1c,0x269,DAT_00420c34);
                  iVar3 = 1;
                }
              }
              else {
                iVar3 = 1;
              }
            }
            else {
              elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420c1c,0x246,DAT_00420c30);
              am_hal_mspi_deinitialize(*puVar2);
            }
          }
          else {
            elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420c1c,0x23f,DAT_00420c2c);
            am_hal_mspi_deinitialize(*puVar2);
          }
        }
        else {
          elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420c1c,0x233,DAT_00420c24);
          am_hal_mspi_deinitialize(*puVar2);
        }
      }
      else {
        elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420c1c,0x22a,DAT_00420b08);
        iVar3 = 1;
      }
    }
  }
  return iVar3;
}

