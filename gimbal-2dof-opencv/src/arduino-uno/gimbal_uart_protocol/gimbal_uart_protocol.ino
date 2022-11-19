#include <Servo.h>

#define IS_DEBUG true

// 舵机配置
#define GPIO_SERVO_DOWN 	9     // 下方舵机的GPIO
#define GPIO_SERVO_UP		10      // 上方舵机的GPIO
#define DEFAULT_ANGLE_DOWN 90.0 // 下方舵机的默认角度
#define DEFAULT_ANGLE_UP 90.0   // 上方舵机的GPIO
#define MIN_ANGLE_DOWN 0.0      // 下方舵机最小角度
#define MAX_ANGLE_DOWN 180.0    // 下方舵机最大角度
#define MIN_ANGLE_UP  0.0       // 上方舵机最小角度
#define MAX_ANGLE_UP 180.0      // 上方舵机最大角度

// 索引定义
#define INVALID_INDEX 255       // 无效索引值

// 舵机定义
Servo servo_down;
Servo servo_up;

// 初始化舵机角度
void init_servo(){
	// 舵机绑定GPIO
	servo_down.attach(GPIO_SERVO_DOWN);
	servo_up.attach(GPIO_SERVO_UP);
	// 角度初始化
	servo_down.write(DEFAULT_ANGLE_DOWN); 
	servo_up.write(DEFAULT_ANGLE_UP);
	// 延时2s
	delay(2);
}

// 更新舵机角度
bool update_servo_angle(){
  // 判断串口是否有数据读入
  if (!Serial.available()){
    return false;
  }
  // 读入一行字符串 末尾是\n
  String str_recv = Serial.readStringUntil('\n');
  if (str_recv.length() <= 0){
    return false;
  }
  // 获取逗号索引
  uint8_t comma_index = str_recv.indexOf(',');
  if (comma_index == INVALID_INDEX){
    return false;
  }
  
  // 提取左侧舵机的角度
  String str_angle_down = str_recv.substring(0, comma_index);
  float angle_down = constrain(str_angle_down.toFloat(), MIN_ANGLE_DOWN, MAX_ANGLE_DOWN);
  // 提取右侧舵机的角度
  String str_angle_up = str_recv.substring(comma_index+1);
  float angle_up = constrain(str_angle_up.toFloat(), MIN_ANGLE_UP, MAX_ANGLE_UP);
  
  // 角度同步
  servo_down.write(angle_down);
  servo_up.write(angle_up);
  
  // 打印接收到的信息
  if (IS_DEBUG){
    Serial.print("Recv:  ");
    Serial.println(str_recv);
    Serial.print("Comma Index: ");
    Serial.println(comma_index);
    Serial.print("Angle Down: ");
    Serial.println(angle_down);
    Serial.print("Angle Up: ");
    Serial.println(angle_up);
  } 
  return true;
}

void setup() {
	// 串口通信初始化
	Serial.begin(115200);
	// 舵机初始
	init_servo();
}

void loop() {
  update_servo_angle();
}
