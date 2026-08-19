import UIKit
@preconcurrency import CoreBluetooth

private func hex(_ data: Data) -> String {
    data.map { String(format: "%02X", $0) }.joined()
}

private func crc16CCITTUpdate(_ initial: UInt16, _ bytes: [UInt8]) -> UInt16 {
    var crc = initial
    for byte in bytes {
        crc = (crc >> 8) | (crc << 8)
        crc ^= UInt16(byte)
        crc ^= (crc & 0x00ff) >> 4
        crc ^= crc << 12
        crc ^= (crc & 0x00ff) << 5
    }
    return crc
}

private func crc16CCITT(_ bytes: [UInt8]) -> UInt16 {
    crc16CCITTUpdate(UInt16.max, bytes)
}

private func crc16MODBUSModel(_ bytes: [UInt8]) -> UInt16 {
    var crc = UInt16.max
    for (index, original) in bytes.enumerated() {
        let byte: UInt8 = (index == 10 || index == 11) ? 0 : original
        crc ^= UInt16(byte)
        for _ in 0..<8 {
            crc = (crc & 1) != 0 ? (crc >> 1) ^ 0xa001 : crc >> 1
        }
    }
    return crc
}

private func crc32Castagnoli(_ bytes: [UInt8]) -> UInt32 {
    var crc: UInt32 = 0
    for byte in bytes {
        crc ^= UInt32(byte) << 24
        for _ in 0..<8 {
            crc = (crc & 0x80000000) != 0
                ? (crc << 1) ^ 0x1edc6f41
                : crc << 1
        }
    }
    return crc
}

private func littleEndianUInt16(_ bytes: [UInt8], _ offset: Int) -> UInt16 {
    UInt16(bytes[offset]) | (UInt16(bytes[offset + 1]) << 8)
}

private func littleEndianUInt32(_ bytes: [UInt8], _ offset: Int) -> UInt32 {
    UInt32(bytes[offset]) |
        (UInt32(bytes[offset + 1]) << 8) |
        (UInt32(bytes[offset + 2]) << 16) |
        (UInt32(bytes[offset + 3]) << 24)
}

private func systemRequest(serial: UInt16, subcommand: UInt8,
                           payload: [UInt8]) -> Data {
    let length = 12 + payload.count
    var model: [UInt8] = [
        100, 1, 100,
        UInt8(truncatingIfNeeded: serial),
        UInt8(truncatingIfNeeded: serial >> 8),
        0, 0, subcommand,
        UInt8(truncatingIfNeeded: length),
        UInt8(truncatingIfNeeded: length >> 8),
        0, 0,
    ] + payload
    let compact = [
        model[0], model[1], model[2], model[3], model[5],
        model[6], model[7], model[8], UInt8(0),
    ]
    let innerCRC = crc16CCITTUpdate(crc16CCITT(compact), payload)
    model[10] = UInt8(truncatingIfNeeded: innerCRC)
    model[11] = UInt8(truncatingIfNeeded: innerCRC >> 8)
    let outerCRC = crc32Castagnoli(model)
    return Data([
        0,
        UInt8(truncatingIfNeeded: outerCRC),
        UInt8(truncatingIfNeeded: outerCRC >> 8),
        UInt8(truncatingIfNeeded: outerCRC >> 16),
        UInt8(truncatingIfNeeded: outerCRC >> 24),
    ] + model)
}

private func pairRolePhoneRequest() -> Data {
    systemRequest(serial: 0x3f00, subcommand: 8, payload: [1])
}

private func deviceInfoRequest() -> Data {
    systemRequest(serial: 0x3f01, subcommand: 2, payload: [])
}

private func deviceStatusRequest(serial: UInt16) -> Data {
    systemRequest(serial: serial, subcommand: 1, payload: [])
}

private func channel1NonmutatingRequest() -> Data {
    // Opcode 0x89 consults byte 3 as command-valid. Zero makes every recovered
    // wear, touch, regulator, secondary-mode, and radio transition unreachable.
    Data([0, 0, 0x89, 0, 0, 0, 0])
}

final class LogViewController: UIViewController {
    private let textView = UITextView()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .black
        textView.translatesAutoresizingMaskIntoConstraints = false
        textView.backgroundColor = .black
        textView.textColor = .green
        textView.font = .monospacedSystemFont(ofSize: 12, weight: .regular)
        textView.isEditable = false
        textView.text = "R1 iPhone diagnostics\n"
        view.addSubview(textView)
        NSLayoutConstraint.activate([
            textView.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor,
                                               constant: 8),
            textView.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor,
                                                constant: -8),
            textView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor,
                                           constant: 8),
            textView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor,
                                              constant: -8),
        ])
    }

    func append(_ message: String) {
        let line = message + "\n"
        print(message)
        fflush(stdout)
        textView.text.append(line)
        if !textView.text.isEmpty {
            textView.scrollRangeToVisible(
                NSRange(location: max(0, textView.text.utf16.count - 1), length: 1))
        }
    }
}

@main
final class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?
    private var probe: RingProbe?

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions:
                        [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        let window = UIWindow(frame: UIScreen.main.bounds)
        let viewController = LogViewController()
        window.rootViewController = viewController
        window.makeKeyAndVisible()
        self.window = window

        let probe = RingProbe(log: viewController.append)
        self.probe = probe
        probe.start()
        return true
    }
}

private final class RingProbe: NSObject,
                               CBCentralManagerDelegate,
                               CBPeripheralDelegate {
    private struct QueuedWrite {
        let data: Data
        let characteristic: CBCharacteristic
        let label: String
    }

    private let log: (String) -> Void
    private var central: CBCentralManager!
    private var ring: CBPeripheral?
    private var channel1RX: CBCharacteristic?
    private var channel1TX: CBCharacteristic?
    private var channel2RX: CBCharacteristic?
    private var channel2TX: CBCharacteristic?
    private var pendingServices = 0
    private var notificationsRequested = false
    private var pairRequestTime: TimeInterval?
    private var deviceInfoRequestTime: TimeInterval?
    private var requestTimes: [UInt16: TimeInterval] = [:]
    private var latencies: [Double] = []
    private var writes: [QueuedWrite] = []
    private var statusSent = 0
    private var statusReceived = 0
    private var channel1Sent = 0
    private var channel1Received = 0
    private var discoveredNames = Set<String>()
    private var finished = false
    private var timeout: DispatchWorkItem?

    init(log: @escaping (String) -> Void) {
        self.log = log
        super.init()
    }

    func start() {
        guard hex(pairRolePhoneRequest()) == "001D47CA7B640164003F0000080D005EB901",
              hex(deviceInfoRequest()) == "0073A36B7B640164013F0000020C001A27",
              hex(deviceStatusRequest(serial: 0x4000)) ==
                "005C2C5C6364016400400000010C00EA3B",
              hex(channel1NonmutatingRequest()) == "00008900000000" else {
            finish("FAIL frame-vector mismatch")
            return
        }
        log("PREFLIGHT exact-frame-vectors=pass mutation-routes=absent")
        central = CBCentralManager(delegate: self, queue: .main)
        let timeout = DispatchWorkItem { [weak self] in
            self?.finish("FAIL timeout")
        }
        self.timeout = timeout
        DispatchQueue.main.asyncAfter(deadline: .now() + 45, execute: timeout)
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        log("BLUETOOTH state=\(central.state.rawValue)")
        guard central.state == .poweredOn else {
            if central.state == .unauthorized || central.state == .unsupported ||
                central.state == .poweredOff {
                finish("FAIL Bluetooth unavailable state=\(central.state.rawValue)")
            }
            return
        }
        log("SCAN target=B56EE2 named-even-observation=true")
        central.scanForPeripherals(withServices: nil,
            options: [CBCentralManagerScanOptionAllowDuplicatesKey: false])
    }

    func centralManager(_ central: CBCentralManager,
                        didDiscover peripheral: CBPeripheral,
                        advertisementData: [String: Any], rssi RSSI: NSNumber) {
        let localName = advertisementData[CBAdvertisementDataLocalNameKey] as? String
        let name = localName ?? peripheral.name ?? ""
        let lower = name.lowercased()
        let relevant = lower.contains("even") || lower.contains("r1") ||
            lower.contains("g1") || lower.contains("glass") ||
            lower.contains("b56ee2")
        if relevant && discoveredNames.insert(name).inserted {
            let serviceCount =
                (advertisementData[CBAdvertisementDataServiceUUIDsKey] as? [CBUUID])?.count ?? 0
            log("NEARBY name=\(name.isEmpty ? "<unnamed>" : name) rssi=\(RSSI) services=\(serviceCount)")
        }
        guard ring == nil, lower.contains("b56ee2") else { return }
        ring = peripheral
        peripheral.delegate = self
        log("MATCH name=\(name) connecting=true")
        central.connect(peripheral)
        DispatchQueue.main.asyncAfter(deadline: .now() + 8) { [weak self] in
            self?.central.stopScan()
        }
    }

    func centralManager(_ central: CBCentralManager,
                        didConnect peripheral: CBPeripheral) {
        log("CONNECTED writeWithResponse=\(peripheral.maximumWriteValueLength(for: .withResponse)) writeWithoutResponse=\(peripheral.maximumWriteValueLength(for: .withoutResponse))")
        peripheral.discoverServices(nil)
    }

    func centralManager(_ central: CBCentralManager,
                        didFailToConnect peripheral: CBPeripheral,
                        error: Error?) {
        finish("FAIL connect \(error?.localizedDescription ?? "unknown")")
    }

    func centralManager(_ central: CBCentralManager,
                        didDisconnectPeripheral peripheral: CBPeripheral,
                        error: Error?) {
        if !finished {
            finish("FAIL disconnected \(error?.localizedDescription ?? "peer closed")")
        }
    }

    func peripheral(_ peripheral: CBPeripheral,
                    didDiscoverServices error: Error?) {
        if let error {
            finish("FAIL service-discovery \(error.localizedDescription)")
            return
        }
        let services = peripheral.services ?? []
        log("SERVICES count=\(services.count) uuids=\(services.map { $0.uuid.uuidString }.joined(separator: ","))")
        pendingServices = services.count
        for service in services {
            peripheral.discoverCharacteristics(nil, for: service)
        }
    }

    func peripheral(_ peripheral: CBPeripheral,
                    didDiscoverCharacteristicsFor service: CBService,
                    error: Error?) {
        if let error {
            finish("FAIL characteristic-discovery \(error.localizedDescription)")
            return
        }
        for characteristic in service.characteristics ?? [] {
            switch characteristic.uuid.uuidString.uppercased() {
            case "BAE80010-4F05-4503-8E65-3AF1F7329D1F":
                channel1RX = characteristic
            case "BAE80011-4F05-4503-8E65-3AF1F7329D1F":
                channel1TX = characteristic
            case "BAE80012-4F05-4503-8E65-3AF1F7329D1F":
                channel2RX = characteristic
            case "BAE80013-4F05-4503-8E65-3AF1F7329D1F":
                channel2TX = characteristic
            default:
                break
            }
            log("CHAR service=\(service.uuid.uuidString) uuid=\(characteristic.uuid.uuidString) properties=0x\(String(characteristic.properties.rawValue, radix: 16))")
        }
        pendingServices -= 1
        if pendingServices == 0 {
            configureBAE8(peripheral)
        }
    }

    private func configureBAE8(_ peripheral: CBPeripheral) {
        guard let channel1RX, let channel1TX, let channel2RX, let channel2TX,
              channel1RX.properties.contains(.writeWithoutResponse),
              channel1TX.properties.contains(.notify),
              channel2RX.properties.contains(.writeWithoutResponse),
              channel2TX.properties.contains(.notify) else {
            finish("FAIL exact BAE8 four-lane contract absent")
            return
        }
        log("BAE8 exact-four-lane-contract=pass")
        notificationsRequested = true
        peripheral.setNotifyValue(true, for: channel1TX)
        peripheral.setNotifyValue(true, for: channel2TX)
    }

    func peripheral(_ peripheral: CBPeripheral,
                    didUpdateNotificationStateFor characteristic: CBCharacteristic,
                    error: Error?) {
        if let error {
            finish("FAIL notify \(error.localizedDescription)")
            return
        }
        log("NOTIFY uuid=\(characteristic.uuid.uuidString) enabled=\(characteristic.isNotifying)")
        guard notificationsRequested,
              channel1TX?.isNotifying == true,
              channel2TX?.isNotifying == true,
              pairRequestTime == nil,
              deviceInfoRequestTime == nil,
              statusSent == 0 else { return }
        enqueue(pairRolePhoneRequest(), on: channel2RX!, label: "pair-role-phone")
        pairRequestTime = ProcessInfo.processInfo.systemUptime
        pumpWrites(peripheral)
    }

    private func enqueue(_ data: Data, on characteristic: CBCharacteristic,
                         label: String) {
        writes.append(QueuedWrite(data: data, characteristic: characteristic,
                                  label: label))
    }

    private func pumpWrites(_ peripheral: CBPeripheral) {
        while peripheral.canSendWriteWithoutResponse && !writes.isEmpty {
            let write = writes.removeFirst()
            peripheral.writeValue(write.data, for: write.characteristic,
                                  type: .withoutResponse)
            log("WRITE label=\(write.label) bytes=\(write.data.count)")
        }
        if !writes.isEmpty {
            log("WRITE-BACKPRESSURE queued=\(writes.count)")
        }
    }

    func peripheralIsReady(toSendWriteWithoutResponse peripheral: CBPeripheral) {
        log("WRITE-READY queued=\(writes.count)")
        pumpWrites(peripheral)
    }

    func peripheral(_ peripheral: CBPeripheral,
                    didUpdateValueFor characteristic: CBCharacteristic,
                    error: Error?) {
        if let error {
            finish("FAIL notification \(error.localizedDescription)")
            return
        }
        guard let value = characteristic.value else { return }
        if characteristic === channel1TX {
            if value == Data([0, 0, 0x89, 0, 1, 0, 0]) {
                channel1Received += 1
                log("CHANNEL1 response=valid count=\(channel1Received)")
            } else {
                log("CHANNEL1 unmatched bytes=\(value.count)")
            }
            return
        }
        guard characteristic === channel2TX else { return }
        handleSystemFragment([UInt8](value), peripheral: peripheral)
    }

    private func handleSystemFragment(_ fragment: [UInt8],
                                      peripheral: CBPeripheral) {
        guard fragment.count >= 17, fragment[0] == 0 else {
            finish("FAIL unexpected channel-2 fragment length=\(fragment.count)")
            return
        }
        let outerObserved = littleEndianUInt32(fragment, 1)
        let model = Array(fragment.dropFirst(5))
        guard crc32Castagnoli(model) == outerObserved,
              model.count >= 12,
              Int(littleEndianUInt16(model, 8)) == model.count,
              crc16MODBUSModel(model) == littleEndianUInt16(model, 10),
              model[0] == 100, model[1] == 1, model[6] == 0 else {
            finish("FAIL channel-2 checksum-or-header")
            return
        }
        let serial = littleEndianUInt16(model, 3)
        let result = model[5] >> 2
        if serial == 0x3f00 && model[7] == 8,
           let started = pairRequestTime {
            let latency = millisecondsSince(started)
            let payload = Array(model.dropFirst(12))
            guard result == 0, payload == [0] else {
                finish("FAIL phone-role refused")
                return
            }
            pairRequestTime = nil
            log(String(format: "PAIR role=phone result=0 latencyMs=%.3f", latency))
            DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
                guard let self, let channel2RX = self.channel2RX else { return }
                self.deviceInfoRequestTime = ProcessInfo.processInfo.systemUptime
                self.enqueue(deviceInfoRequest(), on: channel2RX,
                             label: "device-info")
                self.pumpWrites(peripheral)
            }
            return
        }
        if serial == 0x3f01 && model[7] == 2,
           let started = deviceInfoRequestTime {
            let payload = Array(model.dropFirst(12))
            guard result == 0, payload.count == 32 else {
                finish("FAIL device-info malformed")
                return
            }
            deviceInfoRequestTime = nil
            let application = printableVersion(Array(payload[0..<16]))
            let hardware = printableVersion(Array(payload[16..<32]))
            log(String(format: "IDENTITY application=%@ hardware=%@ latencyMs=%.3f",
                       application, hardware, millisecondsSince(started)))
            startInterleaved(peripheral)
            return
        }
        guard model[7] == 1,
              let started = requestTimes.removeValue(forKey: serial) else {
            log("SYSTEM unmatched serial=\(serial) subcommand=\(model[7])")
            return
        }
        let latency = millisecondsSince(started)
        latencies.append(latency)
        statusReceived += 1
        log(String(format: "STATUS serial=%u result=%u latencyMs=%.3f",
                   serial, result, latency))
        if statusReceived == 20 {
            DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
                self?.complete()
            }
        }
    }

    private func startInterleaved(_ peripheral: CBPeripheral) {
        guard let channel1RX, let channel2RX else {
            finish("FAIL write lanes disappeared")
            return
        }
        log("INTERLEAVED plan=20x20 channel1-command-valid=false")
        for index in 0..<20 {
            let serial = UInt16(0x4000 + index)
            requestTimes[serial] = ProcessInfo.processInfo.systemUptime
            enqueue(deviceStatusRequest(serial: serial), on: channel2RX,
                    label: "status-\(serial)")
            statusSent += 1
            enqueue(channel1NonmutatingRequest(), on: channel1RX,
                    label: "channel1-safe-\(index + 1)")
            channel1Sent += 1
        }
        pumpWrites(peripheral)
    }

    private func complete() {
        let minimum = latencies.min() ?? 0
        let maximum = latencies.max() ?? 0
        let mean = latencies.isEmpty ? 0 : latencies.reduce(0, +) /
            Double(latencies.count)
        log(String(format: "STATUS-SUMMARY sent=%d received=%d dropped=%d minMs=%.3f meanMs=%.3f maxMs=%.3f",
                   statusSent, statusReceived, statusSent - statusReceived,
                   minimum, mean, maximum))
        log("CHANNEL1-SUMMARY sent=\(channel1Sent) observedResponses=\(channel1Received) noObservedResponse=\(channel1Sent - channel1Received)")
        finish(statusReceived == 20 ? "PASS bounded iPhone BLE diagnostics" :
            "FAIL incomplete status responses")
    }

    private func printableVersion(_ bytes: [UInt8]) -> String {
        let significant = bytes.prefix { $0 != 0 && $0 != 0xff }
        return significant.map { byte in
            byte >= 0x20 && byte <= 0x7e ? Character(UnicodeScalar(byte)) : "?"
        }.reduce(into: "") { $0.append($1) }
    }

    private func millisecondsSince(_ start: TimeInterval) -> Double {
        (ProcessInfo.processInfo.systemUptime - start) * 1_000
    }

    private func finish(_ result: String) {
        guard !finished else { return }
        finished = true
        timeout?.cancel()
        central?.stopScan()
        log("RESULT \(result)")
        if let ring, ring.state == .connected {
            central?.cancelPeripheralConnection(ring)
        }
    }
}

