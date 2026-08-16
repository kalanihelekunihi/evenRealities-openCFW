#include "openr1_watchdog_zephyr.h"

#include <errno.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/watchdog.h>
#include <zephyr/kernel.h>

#define OPENR1_WATCHDOG_RELOAD_MILLISECONDS 10000u
#define OPENR1_WATCHDOG_FEED_TICKS 1024u
#define OPENR1_WATCHDOG_STACK_BYTES 512u

static const struct device *const watchdog = DEVICE_DT_GET(DT_NODELABEL(wdt0));
static int watchdog_channel = -1;
static struct k_thread watchdog_thread;
K_THREAD_STACK_DEFINE(watchdog_stack, OPENR1_WATCHDOG_STACK_BYTES);

static void watchdog_timeout(const struct device *device, int channel) {
    (void)device;
    (void)channel;
    /* Match the recovered no-op handler; the hardware reset follows. */
}

static void watchdog_worker(void *first, void *second, void *third) {
    (void)first;
    (void)second;
    (void)third;
    for (;;) {
        (void)wdt_feed(watchdog, watchdog_channel);
        k_sleep(K_TICKS(OPENR1_WATCHDOG_FEED_TICKS));
    }
}

int openr1_watchdog_zephyr_initialize(void) {
    if (k_is_in_isr()) {
        return -EWOULDBLOCK;
    }
    if (watchdog_channel >= 0) {
        return -EALREADY;
    }
    if (!device_is_ready(watchdog)) {
        return -ENODEV;
    }
    const struct wdt_timeout_cfg configuration = {
        .window = {
            .min = 0u,
            .max = OPENR1_WATCHDOG_RELOAD_MILLISECONDS,
        },
        .callback = watchdog_timeout,
        .flags = WDT_FLAG_RESET_SOC,
    };
    int channel = wdt_install_timeout(watchdog, &configuration);
    if (channel < 0) {
        return channel;
    }
    const int error = wdt_setup(watchdog, WDT_OPT_PAUSE_HALTED_BY_DBG);
    if (error != 0) {
        return error;
    }
    watchdog_channel = channel;
    (void)k_thread_create(
        &watchdog_thread, watchdog_stack,
        K_THREAD_STACK_SIZEOF(watchdog_stack), watchdog_worker,
        NULL, NULL, NULL, K_LOWEST_APPLICATION_THREAD_PRIO, 0, K_NO_WAIT);
    (void)k_thread_name_set(&watchdog_thread, "openr1-watchdog");
    return 0;
}
