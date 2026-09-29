
void FUN_004e8970(undefined4 param_1,int param_2)

{
  undefined2 uVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined1 uVar4;
  int iVar5;
  undefined4 uVar6;
  
  puVar2 = DAT_004e9358;
  if (param_2 != 0) {
    FUN_0043c0e4(DAT_004e9358,0xa0,0);
    FUN_00439be4(puVar2,param_1,0xa0);
    puVar3 = DAT_004e935c;
    uVar6 = puVar2[1];
    *DAT_004e935c = *puVar2;
    puVar3[1] = uVar6;
    *(undefined2 *)(puVar3 + 2) = *(undefined2 *)(puVar2 + 2);
    *(undefined2 *)((int)puVar3 + 10) = *(undefined2 *)((int)puVar2 + 10);
    if (6 < *(ushort *)((int)puVar3 + 10)) {
      *(undefined2 *)((int)puVar3 + 10) = 6;
    }
    for (iVar5 = 0; iVar5 < (int)(uint)*(ushort *)((int)puVar3 + 10); iVar5 = iVar5 + 1) {
      *(undefined2 *)((int)puVar3 + iVar5 * 2 + 0xc) =
           *(undefined2 *)((int)puVar2 + iVar5 * 2 + 0xc);
    }
    *(undefined2 *)(puVar3 + 6) = *(undefined2 *)(puVar2 + 6);
    if (6 < *(ushort *)(puVar3 + 6)) {
      *(undefined2 *)(puVar3 + 6) = 6;
    }
    for (iVar5 = 0; iVar5 < (int)(uint)*(ushort *)(puVar3 + 6); iVar5 = iVar5 + 1) {
      *(undefined1 *)((int)puVar3 + iVar5 + 0x1a) = *(undefined1 *)((int)puVar2 + iVar5 + 0x1a);
    }
    FUN_00439c04(puVar3 + 8,puVar2 + 8,0x80);
  }
  puVar2 = DAT_004e9360;
  osMutexAcquire(*DAT_004e9360,0xffffffff);
  uVar1 = *(undefined2 *)((int)DAT_004e935c + 0x2a);
  uVar6 = DAT_004e935c[9];
  uVar4 = *(undefined1 *)(DAT_004e935c + 8);
  osMutexRelease(*puVar2);
  iVar5 = FUN_00466512();
  dashboard_watchface_manager_call_14(uVar6,uVar1,uVar4,iVar5 == 1);
  dashboard_watchface_manager_call_34();
  dashboard_watchface_manager_call_38();
  ui_common_api_fn_00509f86();
  dashboard_watchface_manager_call_1c();
  uVar4 = ui_common_api_fn_00509f8e();
  dashboard_watchface_manager_set_battery(uVar4);
  return;
}

