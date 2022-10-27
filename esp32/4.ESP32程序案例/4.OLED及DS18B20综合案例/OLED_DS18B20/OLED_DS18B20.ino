#include <OneWire.h>
#include <DallasTemperature.h>
#include <U8g2lib.h>
#include <Wire.h>
// SDA接23 SCL接19 VCC接3.3V GND接GND
U8G2_SSD1306_128X64_NONAME_F_SW_I2C u8g2(U8G2_R0,  19, 23, U8X8_PIN_NONE);

#define ONE_WIRE_BUS 5             // 定义DS18B20数据口连接ESP32的 5 脚
OneWire oneWire(ONE_WIRE_BUS);    // 初始连接在单总线上的单总线设备
DallasTemperature sensors(&oneWire);
 
void setup()
{
  u8g2.setI2CAddress(0x3C*2);
  u8g2.begin();
  u8g2.enableUTF8Print();
  Serial.begin(9600);             // 设置串口通信波特率
  sensors.begin();                // 初始库
}
 
void loop(void)
{ 
  u8g2.firstPage();
  do
  {
  sensors.requestTemperatures();  // 发送命令获取温度
  u8g2.setFont(u8g2_font_wqy15_t_chinese1);
  u8g2.setFontPosTop();
  u8g2.setCursor(40,20);
  u8g2.print(String(sensors.getTempCByIndex(0)) + String("摄氏度"));
  }while(u8g2.nextPage());
}
