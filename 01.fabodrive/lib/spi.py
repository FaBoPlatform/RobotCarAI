# coding: utf-8
# SPI 値取得
import spidev
import platform

class SPI():

    # SPIデバイスを保持する
    spi = None

    def __init__(self,bus=None,device=0):
        '''
        /dev/spidevX.Y - X:bus Y:device
        '''
        spi = spidev.SpiDev()

        if bus is None:
            if platform.machine() == 'aarch64':
                bus = 3 # SPI Jetson TX2 /dev/spidev-3.0
            else: # armv7l
                bus = 0 # SPI Raspberry Pi3 /dev/spidev0.0

        spi.open(bus,device)
        spi.max_speed_hz = 5000
        spi.mode = 0b01
        self.spi = spi

        return

    def __del__(self):
        if self.spi is not None:
            # close: Disconnects the object from the interface
            self.spi.close()
        return

    def readadc(self,channel):
        """
        Analog Data Converterの値を読み込む
        channel: SPI_PIN 番号。A0=0, A1=1
        """    
        #Writes a list of values to SPI device.
        #bits_per_word: Property that gets / sets the bits per word.
        #xfer2(list of values[, speed_hz, delay_usec, bits_per_word])
        # SPIから値を取得するための命令設定
        speed_hz = 1
        delay_usec = (8+channel)<<4
        bits_per_word = 0
        to_send = [speed_hz,delay_usec,bits_per_word]

        adc = self.spi.xfer2(to_send)
        data = ((adc[1]&3) << 8) + adc[2]
        return data
