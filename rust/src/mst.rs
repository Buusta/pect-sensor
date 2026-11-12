#![no_std]
#![no_main]

use core::fmt::Write;
use cortex_m::singleton;
use defmt_rtt as _;
use heapless::String;
use panic_probe as _;
use rp_pico as bsp;

use bsp::entry;
use bsp::hal::{clocks::init_clocks_and_plls, pac, sio::Sio, usb::UsbBus, watchdog::Watchdog};
use hal::dma::{double_buffer, DMAExt};
use rp_pico::hal;
use usb_device::{class_prelude::*, prelude::*};
use usbd_serial::SerialPort;
use embedded_hal::pwm::SetDutyCycle;

const TIME_MS: usize = 30;
const BIN_SIZE_US: usize = 5;
const N: usize = TIME_MS * 1000 / BIN_SIZE_US;
const CHUNK: usize = 500; // DMA buffer size, must divide N evenly
const AVERAGES: usize = 1000; // periods to accumulate
const TICKS_PER_MS: u32 = 1250; // 125 MHz / divider 100 = 1.25 MHz tick
const OFF_MS: u32 = 15;         // coil-off time at the start of each period
const PWM_TOP: u16 = (TIME_MS as u32 * TICKS_PER_MS - 1) as u16;
const _: () = assert!(TIME_MS as u32 * TICKS_PER_MS <= 65_536); // max ~52 ms

// calibration samples
const CAL_MS: usize = 1000;
const CAL_CHUNKS: usize = CAL_MS * 1000 / BIN_SIZE_US / CHUNK; // 1000 chunks

// fail the build instead of silently misbehaving
const _: () = assert!(N % CHUNK == 0);
const _: () = assert!(BIN_SIZE_US >= 2); // the ADC can't go faster than 2 us

// 100 KB accumulator in .bss (a static avoids building it on the stack)
static mut ACCUM: [u32; N] = [0; N];

fn send<B: usb_device::bus::UsbBus>(
    usb_dev: &mut UsbDevice<'_, B>,
    serial: &mut SerialPort<'_, B>,
    mut data: &[u8],
) {
    while !data.is_empty() {
        usb_dev.poll(&mut [&mut *serial]);
        match serial.write(data) {
            Ok(n) => data = &data[n..],
            Err(usb_device::UsbError::WouldBlock) => {}
            Err(_) => return,
        }
    }
}

#[entry]
fn main() -> ! {
    let mut pac = pac::Peripherals::take().unwrap();
    let mut watchdog = Watchdog::new(pac.WATCHDOG);
    let sio = Sio::new(pac.SIO);

    let clocks = init_clocks_and_plls(
        12_000_000u32,
        pac.XOSC,
        pac.CLOCKS,
        pac.PLL_SYS,
        pac.PLL_USB,
        &mut pac.RESETS,
        &mut watchdog,
    )
    .ok()
    .unwrap();

    let pins = bsp::Pins::new(
        pac.IO_BANK0,
        pac.PADS_BANK0,
        sio.gpio_bank0,
        &mut pac.RESETS,
    );

    let mut pwm_slices = hal::pwm::Slices::new(pac.PWM, &mut pac.RESETS);
    let pwm = &mut pwm_slices.pwm3;
    pwm.set_div_int(100);
    pwm.set_top(PWM_TOP);
    let channel = &mut pwm.channel_b;
    // channel.output_to(pins.gpio7);
    // channel.set_inverted(); // low first, high until the wrap, so the turn-off edge is the wrap
    channel.set_duty_cycle((OFF_MS * TICKS_PER_MS) as u16).unwrap();
    let mut gate = channel.output_to(pins.gpio7);
    gate.set_slew_rate(hal::gpio::OutputSlewRate::Fast);
    gate.set_drive_strength(hal::gpio::OutputDriveStrength::TwelveMilliAmps);

    // --- USB serial ---
    let usb_bus = UsbBusAllocator::new(UsbBus::new(
        pac.USBCTRL_REGS,
        pac.USBCTRL_DPRAM,
        clocks.usb_clock,
        true,
        &mut pac.RESETS,
    ));
    let mut serial = SerialPort::new(&usb_bus);
    let mut usb_dev = UsbDeviceBuilder::new(&usb_bus, UsbVidPid(0x2e8a, 0x000a))
        .strings(&[StringDescriptors::default()
            .manufacturer("DIY")
            .product("PECT")
            .serial_number("1")])
        .unwrap()
        .device_class(2) // CDC
        .build();

    // wait until the PC has opened the port
    while !serial.dtr() {
        usb_dev.poll(&mut [&mut serial]);
    }

    // --- DMA + ADC ---
    let dma = pac.DMA.split(&mut pac.RESETS);
    let mut adc = hal::Adc::new(pac.ADC, &mut pac.RESETS);
    let mut adc_pin_0 = hal::adc::AdcPin::new(pins.gpio26.into_floating_input()).unwrap();

    let buf_a = singleton!(: [u16; CHUNK] = [0; CHUNK]).unwrap();
    let buf_b = singleton!(: [u16; CHUNK] = [0; CHUNK]).unwrap();
    let accum: &mut [u32; N] = unsafe { &mut *core::ptr::addr_of_mut!(ACCUM) };

    let mut adc_fifo = adc
        .build_fifo()
        // 48 MHz / (95 + 1) = 500 ksps = one sample every 2 us (the ADC's maximum)
        .clock_divider((48 * BIN_SIZE_US - 1) as u16, 0)
        .set_channel(&mut adc_pin_0)
        .enable_dma()
        .start_paused();

    // arm the DMA first, then start the ADC
    let transfer = double_buffer::Config::new(
        (dma.ch0, dma.ch1),
        adc_fifo.dma_read_target(),
        buf_a,
    )
    .start();
    let mut transfer = transfer.write_next(buf_b);


    adc_fifo.resume();

    // --- capture and accumulate ---
    let mut cal_sum: u64 = 0;
    for k in 0..CAL_CHUNKS {
        while !transfer.is_done() {
            usb_dev.poll(&mut [&mut serial]);
        }
        let (buf, next) = transfer.wait();
        if k == CAL_CHUNKS - 1 {
            pwm.enable(); // PWM starts right at a chunk boundary
        }
        for i in 0..CHUNK {
            cal_sum += buf[i] as u64;
        }
        transfer = next.write_next(buf);
    }

    let mut pos = 0usize; // where the next chunk lands in the accumulator
    for _ in 0..(AVERAGES * (N / CHUNK)) {
        while !transfer.is_done() {
            usb_dev.poll(&mut [&mut serial]);
        }
        let (buf, next) = transfer.wait();
        for i in 0..CHUNK {
            accum[pos + i] += buf[i] as u32;
        }
        pos = (pos + CHUNK) % N;
        transfer = next.write_next(buf);
    }

    pwm.disable();

    // --- dump the sums (divide by AVERAGES on the PC) ---
    let b = cal_sum * 1000 / (CAL_CHUNKS * CHUNK) as u64;
    let mut hdr: String<96> = String::new();
    let _ = write!(
        hdr,
        "# baseline_counts={}.{:03} cal_ms={} bin_us={} averages={}\n",
        b / 1000,
        b % 1000,
        CAL_MS,
        BIN_SIZE_US,
        AVERAGES
    );
    send(&mut usb_dev, &mut serial, hdr.as_bytes());

    send(&mut usb_dev, &mut serial, b"time_ms,value\n");

    let mut line: String<32> = String::new();
    for i in 0..N {
        let t_us = (i * BIN_SIZE_US) as u32;
        let avg_x100 = accum[i] as u64 * 100 / AVERAGES as u64;
        line.clear();
        let _ = write!(
            line,
            "{}.{:03},{}.{:02}\n",
            t_us / 1000,
            t_us % 1000,
            avg_x100 / 100,
            avg_x100 % 100
        );
        send(&mut usb_dev, &mut serial, line.as_bytes());
    }

    loop {
        if usb_dev.poll(&mut [&mut serial]) {
            let mut buf = [0u8; 64];
            let _ = serial.read(&mut buf);
        }
    }
}