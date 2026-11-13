#![no_std]
#![no_main]

use defmt_rtt as _;
use panic_probe as _;
use rp_pico as bsp;

use bsp::entry;
use bsp::hal::{clocks::init_clocks_and_plls, pac, usb::UsbBus, watchdog::Watchdog};
use usb_device::{class_prelude::*, prelude::*};
use usbd_serial::SerialPort;
// use heapless::Vec;

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
        if usb_dev.poll(&mut [&mut serial]) {
            let mut buf = [0u8; 64];
            if let Ok(count) = serial.read(&mut buf) {
                if count > 0 {
                    if let Ok(text) = core::str::from_utf8(&buf[..count]) {
                        let reply: &str = match text.trim() {
                            "MEASURE" => "MEASURE OK\n",
                            "PING"    => "PONG\n",
                            _         => "ERR unknown\n",
                        };
                        let _ = serial.write(reply.as_bytes());
                    }
                }
            }
        }
    }
}