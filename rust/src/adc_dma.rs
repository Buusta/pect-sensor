//! Blinks the LED on a Pico board
//!
//! This will blink an LED attached to GP25, which is the pin the Pico uses for the on-board LED.
#![no_std]
#![no_main]

use bsp::entry;
use defmt::*;
use defmt_rtt as _;
use embedded_hal::digital::OutputPin;
use panic_probe as _;


use core::fmt::Write;
use cortex_m::singleton;
// use fugit::RateExtU32;
use hal::dma::{single_buffer, DMAExt};
// use rp2040_hal::Clock;
use rp_pico::hal;

use embedded_hal::pwm::SetDutyCycle;
// use hal::pac;
// Provide an alias for our BSP so we can switch targets quickly.
// Uncomment the BSP you included in Cargo.toml, the rest of the code does not need to change.
use rp_pico as bsp;
// use sparkfun_pro_micro_rp2040 as bsp;

use bsp::hal::{
    clocks::{Clock, init_clocks_and_plls},
    pac,
    sio::Sio,
    watchdog::Watchdog,
};

#[entry]
fn main() -> ! {
    info!("Program start");
    let mut pac = pac::Peripherals::take().unwrap();
    let core = pac::CorePeripherals::take().unwrap();
    let mut watchdog = Watchdog::new(pac.WATCHDOG);
    let sio = Sio::new(pac.SIO);

    // External high-speed crystal on the pico board is 12Mhz
    let external_xtal_freq_hz = 12_000_000u32;
    let clocks = init_clocks_and_plls(
        external_xtal_freq_hz,
        pac.XOSC,
        pac.CLOCKS,
        pac.PLL_SYS,
        pac.PLL_USB,
        &mut pac.RESETS,
        &mut watchdog,
    )
    .ok()
    .unwrap();

    let mut delay = cortex_m::delay::Delay::new(core.SYST, clocks.system_clock.freq().to_Hz());

    let pins = bsp::Pins::new(
        pac.IO_BANK0,
        pac.PADS_BANK0,
        sio.gpio_bank0,
        &mut pac.RESETS,
    );

    // Initialize DMA
    let dma = pac.DMA.split(&mut pac.RESETS);

    // Enable ADC
    let mut adc = hal::Adc::new(pac.ADC, &mut pac.RESETS);

    // Enable the temperature sense channel
    let mut temperature_sensor = adc.take_temp_sensor().unwrap();

    // we'll capture 1000 samples in total
    // NOTE: when calling `shift_8bit` below, the type here must be changed from `u16` to `u8`
    let buf_for_samples = singleton!(: [u16; 512] = [0; 512]).unwrap();

    // Configure free-running mode:
    let mut adc_fifo = adc
        .build_fifo()
        // Set clock divider to target a sample rate of 1000 samples per second (1ksps).
        // The value was calculated by `(48MHz / 1ksps) - 1 = 47999.0`.
        // Please check the `clock_divider` method documentation for details.
        .clock_divider(47999, 0)
        // sample the temperature sensor first
        .set_channel(&mut temperature_sensor)
        // Uncomment this line to produce 8-bit samples, instead of 12 bit (lower bits are discarded)
        //.shift_8bit()
        // Enable DMA transfers for the FIFO
        .enable_dma()
        // Create the FIFO, but don't start it just yet
        .start_paused();

    // Start a DMA transfer (must happen before resuming the ADC FIFO)
    let dma_transfer =
        single_buffer::Config::new(dma.ch0, adc_fifo.dma_read_target(), buf_for_samples).start();

    // Resume the FIFO to start capturing
    adc_fifo.resume();

    // initialize a timer, to measure the total sampling time (printed below)
    let timer = hal::Timer::new(pac.TIMER, &mut pac.RESETS, &clocks);


    // the DMA unit takes care of shuffling data from the FIFO into the buffer.
    // We just sit here and wait... 😴
    let (_ch, _adc_read_target, buf_for_samples) = dma_transfer.wait();

    // ^^^ the three results here (channel, adc::DmaReadTarget, write target) can be reused
    // right away to start another transfer.

    let time_taken = timer.get_counter();

    // Stop free-running mode (the returned `adc` can be reused for future captures)
    let _adc = adc_fifo.stop();

    loop {
        delay.delay_ms(500);
    }
}

// End of file
