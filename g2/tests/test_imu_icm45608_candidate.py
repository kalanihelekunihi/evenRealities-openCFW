import ctypes
import math
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/imu_icm45608.c"
FIXTURE = ROOT / "tests/fixtures/imu_icm45608_host.c"
HEADER = ROOT / "tests/fixtures/imu_icm45608_host.h"


class Mode(ctypes.Structure):
    _fields_ = [
        ("features", ctypes.c_uint8), ("reserved", ctypes.c_uint8 * 3),
        ("period_us", ctypes.c_uint32), ("fifo_watermark", ctypes.c_uint32),
        ("interrupt_period", ctypes.c_uint32),
    ]


class Sample(ctypes.Structure):
    _fields_ = [
        ("timestamp", ctypes.c_uint32), ("flags", ctypes.c_uint8),
        ("reserved_05", ctypes.c_uint8), ("accel_raw", ctypes.c_int16 * 3),
        ("gyro_raw", ctypes.c_int16 * 3), ("mag_raw", ctypes.c_int16 * 3),
        ("quaternion_q30", ctypes.c_int32 * 4), ("accel", ctypes.c_float * 3),
        ("gyro", ctypes.c_float * 3), ("magnetic", ctypes.c_float * 3),
        ("quaternion", ctypes.c_float * 4), ("euler", ctypes.c_float * 3),
        ("reserved_68", ctypes.c_uint8 * 4),
        ("compass_valid", ctypes.c_uint8),
        ("compass_calibrated", ctypes.c_uint8),
        ("reserved_6e", ctypes.c_uint8 * 2),
    ]


class Ring(ctypes.Structure):
    _fields_ = [
        ("start_timestamp", ctypes.c_uint32),
        ("first_index", ctypes.c_uint32), ("count", ctypes.c_uint32),
        ("sample", Sample * 20),
    ]


class ImuCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temp.name) / "imu.so"
        subprocess.run([
            "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
            "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
            str(SOURCE), str(FIXTURE), "-o", str(cls.library),
        ], check=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_imu_filter_update.restype = ctypes.c_float
        cls.lib.open_cfw_imu_filter_update.argtypes = [ctypes.c_float, ctypes.c_void_p]
        cls.lib.open_cfw_imu_apply_odr_config.argtypes = [ctypes.POINTER(Mode)]
        cls.lib.open_cfw_imu_apply_odr_config.restype = ctypes.c_int32
        cls.lib.open_cfw_imu_initialize.argtypes = [ctypes.c_uint8]
        cls.lib.open_cfw_imu_initialize.restype = ctypes.c_int32
        cls.lib.open_cfw_imu_read_data.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_imu_read_data.restype = ctypes.c_int32
        cls.lib.open_cfw_imu_set_orientation_matrix.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_float)]
        cls.lib.open_cfw_imu_quaternion_to_euler.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
        cls.lib.open_cfw_imu_normalize_heading.restype = ctypes.c_int32
        cls.lib.open_cfw_imu_get_heading_degrees.restype = ctypes.c_int32
        cls.lib.open_cfw_imu_get_heading_float.restype = ctypes.c_float
        cls.lib.open_cfw_imu_read_who_am_i.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.open_cfw_mag_read_who_am_i.argtypes = [ctypes.POINTER(ctypes.c_uint32)]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def scalar(self, kind, name):
        return kind.in_dll(self.lib, name)

    def array(self, kind, name):
        return kind.in_dll(self.lib, name)

    def ring(self):
        words = (ctypes.c_uint64 * 282).in_dll(self.lib, "host_imu_ring_words")
        return ctypes.cast(words, ctypes.POINTER(Ring)).contents

    def setUp(self):
        self.lib.host_imu_reset()

    def test_recovered_layout_is_exact(self):
        self.assertEqual(ctypes.sizeof(Sample), 0x70)
        self.assertEqual(Sample.accel.offset, 0x28)
        self.assertEqual(Sample.gyro.offset, 0x34)
        self.assertEqual(Sample.magnetic.offset, 0x40)
        self.assertEqual(Sample.euler.offset, 0x5C)
        self.assertEqual(Sample.compass_valid.offset, 0x6C)
        self.assertEqual(Ring.sample.offset, 12)

    def test_bus_transport_and_failure_mapping(self):
        data = (ctypes.c_uint8 * 4)()
        self.lib.open_cfw_imu_bus_read.argtypes = [
            ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]
        self.lib.open_cfw_imu_bus_write.argtypes = [
            ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]
        self.assertEqual(self.lib.open_cfw_imu_bus_read(0x72, data, 4), 0)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_i2c_bus").value, 4)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_i2c_address").value, 0x69)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_i2c_count").value, 1)
        self.scalar(ctypes.c_int32, "host_imu_i2c_write_status").value = 3
        self.assertEqual(self.lib.open_cfw_imu_bus_write(0x10, data, 4), -1)

    def test_odr_policy_and_initialization_errors(self):
        mode = Mode(3, (ctypes.c_uint8 * 3)(), 10000, 12, 25)
        self.assertEqual(self.lib.open_cfw_imu_apply_odr_config(ctypes.byref(mode)), 0)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_odr_accel").value, 9)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_odr_index").value, 2)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_fifo_watermark").value, 12)
        mode.period_us = 1234
        self.assertEqual(self.lib.open_cfw_imu_apply_odr_config(ctypes.byref(mode)), -1)
        self.assertEqual(self.lib.open_cfw_imu_initialize(5), -1)
        self.assertEqual(self.lib.open_cfw_imu_initialize(2), 0)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_mode").value, 2)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_power_count").value, 2)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_configure_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_configure_accel_odr").value, 9)
        self.assertEqual(self.scalar(ctypes.c_uint16, "host_imu_configure_watermark").value, 8)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_configure_fusion_enabled").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_configure_extended_enabled").value, 1)
        mounting = self.array(ctypes.c_int8 * 9, "host_imu_configure_mounting_matrix")
        self.assertEqual(tuple(mounting), (1, 0, 0, 0, 1, 0, 0, 0, 1))
        self.scalar(ctypes.c_int32, "host_imu_i2c_write_status").value = 7
        self.assertEqual(self.lib.open_cfw_imu_initialize(1), -1)

    def test_source_owned_device_init_and_exact_public_abi(self):
        registers = self.array(ctypes.c_uint8 * 256, "host_imu_registers")
        registers[0x2D] = 0x35
        registers[0x32] = 0xA7
        registers[0x24] = 0x05
        registers[0x18] = 0xFE
        self.assertEqual(self.lib.open_cfw_imu_device_context_init(), 0)
        self.assertEqual(registers[0x2D], 0x35)
        self.assertEqual(registers[0x32], 0xA7)
        self.assertEqual(registers[0x18] & 0x07, 0x01)
        registers[0x72] = 0
        self.assertEqual(self.lib.open_cfw_imu_device_context_init(), -1)
        registers[0x72] = 0x81
        registers[0x19] = 0
        self.assertEqual(self.lib.open_cfw_imu_device_context_init(), -1)

    def test_orientation_fixed_point_and_quaternion_math(self):
        matrix = (ctypes.c_float * 9)(1, 0, 0, 0, 1, 0, 0, 0, 1)
        self.assertEqual(self.lib.open_cfw_imu_set_orientation_matrix(0, 0, matrix), 0)
        q14 = self.array(ctypes.c_int16 * 9, "host_imu_orientation_q14")
        q30 = self.array(ctypes.c_int32 * 9, "host_imu_orientation_q30")
        self.assertEqual((q14[0], q14[4], q14[8]), (16384, 16384, 16384))
        self.assertEqual((q30[0], q30[4], q30[8]), (-1073741824, -1073741824, 1073741824))
        quaternion = (ctypes.c_float * 4)(1, 0, 0, 0)
        euler = (ctypes.c_float * 3)()
        self.assertEqual(self.lib.open_cfw_imu_quaternion_to_euler(quaternion, euler), 0)
        self.assertTrue(all(abs(value) < 0.01 for value in euler))
        vector = (ctypes.c_float * 3)(1, 2, 3)
        self.lib.open_cfw_imu_transform_vector(vector, matrix)
        self.assertEqual(tuple(vector), (1.0, 2.0, 3.0))

    def test_fifo_parser_scales_accel_and_gyro(self):
        packet = (ctypes.c_uint8 * 41)()
        packet[0] = 3
        for offset, value in zip((6, 8, 10), (8192, -4096, 2048)):
            packet[offset:offset + 2] = struct.pack("<h", value)
        for offset, value in zip((12, 14, 16), (16, -16, 8)):
            packet[offset:offset + 2] = struct.pack("<h", value)
        self.ring().start_timestamp = 500
        self.lib.open_cfw_imu_data_parser_callback(packet)
        ring = self.ring()
        self.assertEqual(ring.count, 1)
        sample = ring.sample[0]
        self.assertEqual(sample.timestamp, 500)
        self.assertEqual(sample.flags & 3, 3)
        self.assertAlmostEqual(sample.accel[0], 1.0, places=5)
        self.assertAlmostEqual(sample.accel[1], -0.5, places=5)
        self.assertAlmostEqual(sample.gyro[0], 64000 / 65536, places=5)

    def test_read_data_routes_fifo_and_register_polling(self):
        fifo = self.array(ctypes.c_uint8 * 2048, "host_imu_fifo_mirror")
        fifo[0] = 3
        fifo[6:8] = struct.pack("<h", 8192)
        fifo[12:14] = struct.pack("<h", 16)
        self.scalar(ctypes.c_uint16, "host_imu_fifo_frame_count").value = 1
        self.assertEqual(self.lib.open_cfw_imu_read_data(700), 0)
        self.assertEqual(self.ring().sample[0].timestamp, 700)
        self.assertEqual(self.ring().sample[0].flags & 3, 3)

        self.lib.host_imu_reset()
        poll = self.array(ctypes.c_uint8 * 41, "host_imu_poll_packet")
        poll[0] = 1
        poll[6:8] = struct.pack("<h", 4096)
        self.scalar(ctypes.c_uint8, "host_imu_poll_has_packet").value = 1
        self.assertEqual(self.lib.open_cfw_imu_read_data(900), 0)
        self.assertEqual(self.ring().sample[0].timestamp, 900)
        self.assertEqual(self.ring().sample[0].flags & 1, 1)

        self.lib.host_imu_reset()
        self.scalar(ctypes.c_uint8, "host_imu_extended_events").value = 0x0d
        self.scalar(ctypes.c_uint8, "host_imu_extended_aid_human").value = 6
        self.scalar(ctypes.c_uint8, "host_imu_extended_aid_device").value = 6
        self.assertEqual(self.lib.open_cfw_imu_read_data(1000), 0)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_aid_enabled").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_aid_changed_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_event_id").value, 6)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_extended_read_count").value, 1)

    def test_fusion_parser_populates_magnetic_quaternion_and_compass(self):
        packet = (ctypes.c_uint8 * 41)()
        packet[0] = 0x30
        fusion = self.array(ctypes.c_uint8 * 84, "host_imu_fusion_result")
        for offset, value in zip((0, 2, 4, 6), (16384, 0, 0, 0)):
            fusion[offset:offset + 2] = struct.pack("<h", value)
        fusion[8] = 1
        for offset, value in zip((48, 50, 52), (100, -50, 25)):
            fusion[offset:offset + 2] = struct.pack("<h", value)
        fusion[54] = 1
        fusion[68] = 2
        fusion[70] = 1
        fusion[81] = 1
        self.scalar(ctypes.c_int32, "host_imu_fusion_status").value = 0
        self.lib.open_cfw_imu_data_parser_callback(packet)
        sample = self.ring().sample[0]
        self.assertEqual(sample.flags & 0x28, 0x28)
        self.assertAlmostEqual(sample.quaternion[0], 1.0, places=5)
        self.assertEqual(sample.compass_valid, 1)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_compass_ready").value, 1)

    def test_aid_heading_and_head_up_event_policy(self):
        self.assertEqual(self.lib.open_cfw_imu_aid_state_update(6, 6), 0)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_aid_enabled").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_aid_changed_count").value, 1)
        self.assertEqual(self.lib.open_cfw_imu_aid_state_update(1, 1), 0)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_aid_enabled").value, 0)
        self.assertEqual(self.lib.open_cfw_imu_normalize_heading(-10), 350)
        ring = self.ring(); ring.count = 1; ring.sample[0].flags = 0x20; ring.sample[0].euler[2] = 45
        self.assertEqual(self.lib.open_cfw_imu_check_head_up_event(), 0)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_event_id").value, 6)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_head_up_armed").value, 0)

    def test_latest_complete_sample_and_scalar_state(self):
        ring = self.ring(); ring.count = 1
        for axis, values in enumerate(((1, 2, 3), (4, 5, 6), (7, 8, 9))):
            ring.sample[0].gyro[axis] = values[0]
            ring.sample[0].accel[axis] = values[1]
            ring.sample[0].magnetic[axis] = values[2]
        self.lib.open_cfw_imu_get_latest_complete_sample.restype = ctypes.POINTER(ctypes.c_float)
        result = self.lib.open_cfw_imu_get_latest_complete_sample()
        self.assertEqual(tuple(result[index] for index in range(9)),
                         (1, 4, 7, 2, 5, 8, 3, 6, 9))
        self.lib.open_cfw_imu_set_heading(ctypes.c_float(371.4))
        self.assertAlmostEqual(self.lib.open_cfw_imu_get_heading_float(), 371.4, places=3)
        self.assertEqual(self.lib.open_cfw_imu_get_heading_degrees(), 11)
        self.lib.open_cfw_imu_set_state_two(1)
        self.assertEqual(self.lib.open_cfw_imu_get_state_two(), 1)

    def test_raw_csv_lifecycle_timeout_and_identity(self):
        self.scalar(ctypes.c_uint32, "host_imu_tick").value = 1000
        self.assertEqual(self.lib.open_cfw_imu_start_raw_data_collection(), 0)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_raw_active").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_raw_handle").value, 7)
        path = bytes(self.array(ctypes.c_char * 32, "host_imu_raw_last_path")).split(b"\0", 1)[0]
        self.assertEqual(path, b"/log/imu_rawdata_001000.csv")
        self.scalar(ctypes.c_uint32, "host_imu_tick").value = 121000
        self.assertEqual(self.lib.open_cfw_imu_save_raw_data_to_csv(), 0)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_imu_raw_active").value, 0)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_imu_raw_close_count").value, 1)
        who = ctypes.c_uint32(); mag = ctypes.c_uint32()
        self.assertEqual(self.lib.open_cfw_imu_read_who_am_i(ctypes.byref(who)), 0)
        self.assertEqual(self.lib.open_cfw_mag_read_who_am_i(ctypes.byref(mag)), 0)
        self.assertEqual((who.value, mag.value), (0x81, 0x90))
        self.assertEqual(self.lib.open_cfw_imu_read_who_am_i(None), -1)

    def test_all_target_selectors_compile_strictly(self):
        with tempfile.TemporaryDirectory() as directory:
            for selector in range(1, 55):
                output = Path(directory) / f"imu-{selector}.o"
                subprocess.run([
                    "/usr/bin/clang", "--target=arm-none-eabi",
                    "-mcpu=cortex-m55", "-mthumb", "-mfloat-abi=hard",
                    "-mfpu=fpv5-d16", "-ffreestanding", "-fno-builtin",
                    "-fno-stack-protector", "-Oz", "-std=c11", "-Wall",
                    "-Wextra", "-Werror", f"-DOPEN_CFW_IMU_SELECTOR={selector}",
                    "-c", str(SOURCE), "-o", str(output),
                ], check=True)
                self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
