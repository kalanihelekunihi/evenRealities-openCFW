
/* WARNING: Removing unreachable block (ram,0x0048e266) */
/* WARNING: Removing unreachable block (ram,0x0048e2a8) */
/* WARNING: Removing unreachable block (ram,0x0048e26e) */
/* WARNING: Removing unreachable block (ram,0x0048e298) */
/* WARNING: Removing unreachable block (ram,0x0048e272) */

undefined4 thread_notification_drain_queue(void)

{
  osMessageQueueGet(*(undefined4 *)(DAT_0048e444 + 0xc),&stack0xfffffff8,0,0);
  return 0;
}

