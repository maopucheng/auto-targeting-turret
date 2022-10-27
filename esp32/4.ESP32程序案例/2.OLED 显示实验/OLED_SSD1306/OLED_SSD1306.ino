
#include <U8g2lib.h>
#include <Wire.h>
// SDA接23 SCL接19 VCC接3.3V GND接GND
U8G2_SSD1306_128X64_NONAME_F_SW_I2C u8g2(U8G2_R0,  19, 23, U8X8_PIN_NONE);

void setup(){
  u8g2.setI2CAddress(0x3C*2);
  u8g2.begin();
  u8g2.enableUTF8Print();

}

void loop(){
  u8g2.firstPage();
  do
  {
    u8g2.setFont(u8g2_font_wqy15_t_chinese1);
    u8g2.setFontPosTop();
    u8g2.setCursor(0,20);
    u8g2.print("你好!ESP32");
  }while(u8g2.nextPage());

}
