import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/drv_gx8002b.c"
FIXTURE = ROOT / "tests/fixtures/drv_gx8002b_host.c"
HEADER = ROOT / "tests/fixtures/drv_gx8002b_host.h"


class DrvGx8002bCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.libs = {}
        for selector in range(1, 13):
            output = Path(cls.temp.name) / f"gx8002b-{selector}.so"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
                "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
                f"-DOPEN_CFW_SELECTOR={selector}", str(SOURCE), str(FIXTURE),
                "-o", str(output),
            ], check=True)
            cls.libs[selector] = ctypes.CDLL(str(output))
            cls.libs[selector].host_gx_reset()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @staticmethod
    def word(lib, name):
        return ctypes.c_uint32.in_dll(lib, name)

    @staticmethod
    def byte(lib, name):
        return ctypes.c_uint8.in_dll(lib, name)

    @staticmethod
    def calls(lib):
        count = ctypes.c_uint32.in_dll(lib, "host_gx_call_count").value
        return list((ctypes.c_uint32 * 64).in_dll(lib, "host_gx_calls"))[:count]

    def setUp(self):
        for lib in self.libs.values():
            lib.host_gx_reset()

    def test_nvic_enable_and_disable_match_cmsis_word_selection_and_barriers(self):
        enable, disable = self.libs[1], self.libs[2]
        enable.open_cfw_gx8002_nvic_enable(44)
        iser = (ctypes.c_uint32 * 16).in_dll(enable, "host_gx_iser")
        self.assertEqual(iser[1], 1 << 12)
        before = list(iser)
        enable.open_cfw_gx8002_nvic_enable(-1)
        self.assertEqual(list(iser), before)

        disable.open_cfw_gx8002_nvic_disable(65)
        icer = (ctypes.c_uint32 * 16).in_dll(disable, "host_gx_icer")
        self.assertEqual(icer[2], 2)
        self.assertEqual(self.calls(disable), [1, 2])
        disable.host_gx_reset()
        disable.open_cfw_gx8002_nvic_disable(-12)
        self.assertEqual(self.calls(disable), [])

    def test_nvic_priority_handles_external_and_system_irqs(self):
        lib = self.libs[3]
        lib.open_cfw_gx8002_nvic_set_priority(44, 4)
        ipr = (ctypes.c_uint8 * 512).in_dll(lib, "host_gx_ipr")
        self.assertEqual(ipr[44], 0x40)
        lib.open_cfw_gx8002_nvic_set_priority(-12, 7)
        shpr = (ctypes.c_uint8 * 32).in_dll(lib, "host_gx_shpr_storage")
        self.assertEqual(shpr[4], 0x70)
        lib.open_cfw_gx8002_nvic_set_priority(-1, 31)
        self.assertEqual(shpr[15], 0xF0)

    def test_isr_status_clear_service_order_and_rx_notification_gate(self):
        lib = self.libs[4]
        self.word(lib, "host_gx_interrupt_status_value").value = 0x10
        lib.open_cfw_gx8002_i2s_isr()
        self.assertEqual(self.calls(lib), [18, 19, 20])
        self.assertEqual(self.word(lib, "host_gx_rx_notify_count").value, 1)
        lib.host_gx_reset()
        self.word(lib, "host_gx_interrupt_status_value").value = 0x80
        lib.open_cfw_gx8002_i2s_isr()
        self.assertEqual(self.word(lib, "host_gx_rx_notify_count").value, 0)

    def test_power_on_and_off_are_idempotent_and_preserve_gpio_delay_order(self):
        on, off = self.libs[5], self.libs[6]
        on.open_cfw_gx8002_power_on()
        self.assertEqual(self.byte(on, "host_gx_power_state").value, 1)
        count = self.word(on, "host_gx_gpio_count").value
        pins = list((ctypes.c_uint32 * 8).in_dll(on, "host_gx_gpio_index"))[:count]
        values = list((ctypes.c_uint32 * 8).in_dll(on, "host_gx_gpio_value"))[:count]
        delays = list((ctypes.c_uint32 * 8).in_dll(on, "host_gx_delays"))[:2]
        self.assertEqual((pins, values, delays), ([6, 7, 8], [1, 1, 1], [5, 20]))
        on.open_cfw_gx8002_power_on()
        self.assertEqual(self.word(on, "host_gx_gpio_count").value, 3)

        self.byte(off, "host_gx_power_state").value = 1
        off.open_cfw_gx8002_power_off()
        self.assertEqual(self.byte(off, "host_gx_power_state").value, 0)
        self.assertEqual(list((ctypes.c_uint32 * 8).in_dll(off, "host_gx_gpio_index"))[:3], [6, 7, 8])
        self.assertEqual(list((ctypes.c_uint32 * 8).in_dll(off, "host_gx_gpio_value"))[:3], [0, 0, 0])
        off.open_cfw_gx8002_power_off()
        self.assertEqual(self.word(off, "host_gx_gpio_count").value, 3)

    def test_power_state_accessor_returns_cached_byte(self):
        lib = self.libs[7]
        lib.open_cfw_gx8002_power_state_get.restype = ctypes.c_uint8
        self.byte(lib, "host_gx_power_state").value = 0xA5
        self.assertEqual(lib.open_cfw_gx8002_power_state_get(), 0xA5)

    def test_i2s_init_is_idempotent_and_matches_complete_provider_order(self):
        lib = self.libs[8]
        lib.open_cfw_gx8002_i2s_init()
        self.assertEqual(self.byte(lib, "host_gx_i2s_state").value, 1)
        self.assertEqual(self.calls(lib), [3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.assertEqual(ctypes.c_void_p.in_dll(lib, "host_gx_i2s_handle").value, 0x22220000)
        self.assertEqual(ctypes.c_int32.in_dll(lib, "host_gx_last_irq").value, 44)
        self.assertEqual(self.word(lib, "host_gx_last_priority").value, 4)
        lib.open_cfw_gx8002_i2s_init()
        self.assertEqual(len(self.calls(lib)), 10)

    def test_i2s_deinit_is_idempotent_and_matches_complete_provider_order(self):
        lib = self.libs[9]
        lib.open_cfw_gx8002_i2s_deinit()
        self.assertEqual(self.calls(lib), [])
        self.byte(lib, "host_gx_i2s_state").value = 1
        lib.open_cfw_gx8002_i2s_deinit()
        self.assertEqual(self.byte(lib, "host_gx_i2s_state").value, 0)
        self.assertEqual(self.calls(lib), [13, 14, 15, 16, 17])
        lib.open_cfw_gx8002_i2s_deinit()
        self.assertEqual(len(self.calls(lib)), 5)

    def test_rx_buffer_query_invalidates_exact_3200_byte_descriptor(self):
        lib = self.libs[10]
        lib.open_cfw_gx8002_i2s_rx_buffer_get.argtypes = [
            ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint32)]
        buffer = ctypes.c_void_p()
        length = ctypes.c_uint32()
        self.word(lib, "host_gx_dma_buffer_value").value = 0x20005678
        lib.open_cfw_gx8002_i2s_rx_buffer_get(ctypes.byref(buffer), ctypes.byref(length))
        self.assertEqual((buffer.value, length.value), (0x20005678, 3200))
        self.assertEqual(ctypes.c_size_t.in_dll(lib, "host_gx_cache_address").value, 0x20005678)
        self.assertEqual(self.word(lib, "host_gx_cache_length").value, 3200)
        self.assertEqual(self.word(lib, "host_gx_cache_clean").value, 0)
        self.assertEqual(self.calls(lib), [21])

    def test_audio_notify_wrapper_is_exact(self):
        lib = self.libs[11]
        lib.open_cfw_gx8002_audio_thread_notify()
        self.assertEqual(self.word(lib, "host_gx_audio_notify_count").value, 1)

    def test_reboot_power_cycles_and_optionally_skips_boot_wait(self):
        lib = self.libs[12]
        lib.open_cfw_gx8002_reboot.argtypes = [ctypes.c_bool]
        lib.open_cfw_gx8002_reboot(False)
        self.assertEqual((self.word(lib, "host_gx_power_off_count").value,
                          self.word(lib, "host_gx_power_on_count").value), (1, 1))
        self.assertEqual(list((ctypes.c_uint32 * 8).in_dll(lib, "host_gx_delays"))[:2], [100, 1500])
        lib.host_gx_reset()
        lib.open_cfw_gx8002_reboot(True)
        self.assertEqual(list((ctypes.c_uint32 * 8).in_dll(lib, "host_gx_delays"))[:1], [100])

    def test_all_target_selectors_compile_strictly(self):
        for selector in range(1, 13):
            output = Path(self.temp.name) / f"gx8002b-{selector}.o"
            subprocess.run([
                "/usr/bin/clang", "-target", "arm-none-eabi", "-mthumb",
                "-mcpu=cortex-m55", "-std=c11", "-O2", "-ffreestanding",
                "-fno-builtin", "-fropi", "-Wall", "-Wextra", "-Werror",
                f"-DOPEN_CFW_SELECTOR={selector}", "-c", str(SOURCE),
                "-o", str(output),
            ], check=True)


if __name__ == "__main__":
    unittest.main()
