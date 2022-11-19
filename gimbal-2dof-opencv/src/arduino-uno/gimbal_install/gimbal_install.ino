/* 舵机云台初始化安装 */
#include <Servo.h>

// 舵机配置
#define GPIO_SERVO_DOWN 	9    // 下方舵机的GPIO
#define GPIO_SERVO_UP		10     // 上方舵机的GPIO
#define DEFAULT_ANGLE_DOWN 90.0 // 下方舵机的默认角度
#define DEFAULT_ANGLE_UP 90.0   // 上方舵机的GPIO

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


void setup() {

	// 舵机初始
	init_servo();
}

void loop() {
}
