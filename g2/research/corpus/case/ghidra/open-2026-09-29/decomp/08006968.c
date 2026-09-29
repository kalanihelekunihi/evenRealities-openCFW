
void app_rtos_init(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = os_timer_or_thread_create_wrapper(DAT_08006a14,0,0,DAT_08006a10);
  iVar2 = DAT_08006a18;
  iVar1 = DAT_08006a10;
  *(undefined4 *)(DAT_08006a18 + 0x10) = uVar3;
  uVar3 = os_timer_or_thread_create_wrapper(DAT_08006a1c,1,0,iVar1 + 0x20);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x18) = uVar3;
  uVar3 = os_timer_or_thread_create_wrapper(DAT_08006a20,1,0,iVar1 + 0x30);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x1c) = uVar3;
  uVar3 = os_timer_or_thread_create_wrapper(DAT_08006a24,1,0,iVar1 + 0x40);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x20) = uVar3;
  uVar3 = os_timer_or_thread_create_wrapper(DAT_08006a28,0,0,iVar1 + 0x10);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x14) = uVar3;
  uVar3 = os_timer_or_thread_create_wrapper(DAT_08006a2c,0,0,iVar1 + 0x50);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x24) = uVar3;
  uVar3 = os_timer_or_thread_create_wrapper(DAT_08006a30,0,iVar1 + 0x84);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x2c) = uVar3;
  uVar3 = os_timer_or_thread_create_wrapper(DAT_08006a34,0,iVar1 + 0xa8);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x30) = uVar3;
  uVar3 = os_timer_or_thread_create_wrapper(DAT_08006a38,0,iVar1 + 0xcc);
  iVar1 = DAT_08006a10;
  *(undefined4 *)(iVar2 + 0x34) = uVar3;
  uVar3 = os_timer_or_thread_create_wrapper(DAT_08006a3c,0,iVar1 + 0x60);
  *(undefined4 *)(iVar2 + 0x28) = uVar3;
  uVar3 = os_event_flags_create_wrapper(DAT_08006a10 + 0xf0);
  *(undefined4 *)(iVar2 + 0x38) = uVar3;
  return;
}

