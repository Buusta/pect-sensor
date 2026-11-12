#![no_std]
#![no_main]

use defmt_rtt as _;
use panic_probe as _;
use rp_pico as bsp;

use bsp::entry;
use bsp::hal::{clocks::init_clocks_and_plls, pac, usb::UsbBus, watchdog::Watchdog};
use usb_device::{class_prelude::*, prelude::*};
use usbd_serial::SerialPort;
use heapless::Vec;

#[entry]
fn main() -> ! {
    let mut pac = pac::Peripherals::take().unwrap();
    let mut watchdog = Watchdog::new(pac.WATCHDOG);

    let clocks = init_clocks_and_plls(
        bsp::XOSC_CRYSTAL_FREQ,
        pac.XOSC,
        pac.CLOCKS,
        pac.PLL_SYS,
        pac.PLL_USB,
        &mut pac.RESETS,
        &mut watchdog,
    )
    .ok()
    .unwrap();

    let usb_bus = UsbBusAllocator::new(UsbBus::new(
        pac.USBCTRL_REGS,
        pac.USBCTRL_DPRAM,
        clocks.usb_clock,
        true,
        &mut pac.RESETS,
    ));

    let mut serial = SerialPort::new(&usb_bus);

    let mut usb_dev = UsbDeviceBuilder::new(&usb_bus, UsbVidPid(0x16c0, 0x27dd))
        .strings(&[StringDescriptors::default()
            .manufacturer("GuusH, OscarB")
            .product("PEC sensor")
            .serial_number("0001")])
        .unwrap()
        .device_class(2) // CDC
        .build();

    loop {
        // must be called often, it's what actually runs USB
        if usb_dev.poll(&mut [&mut serial]) {
            let mut buf = [0u8; 64];
            if let Ok(count) = serial.read(&mut buf) {
                if count > 0 {
                    let mut msg: Vec<u8, 128> = Vec::new();
                    let _ = msg.extend_from_slice(&buf[..count]);
                    let _ = msg.extend_from_slice(b"\nI suck at programming\n");

                    let mut out = &msg[..];
                    while !out.is_empty() {
                        match serial.write(out) {
                            Ok(n) => out = &out[n..],
                            Err(_) => break,
                        }
                    }
                }
            }
        }
    }
}