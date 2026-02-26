#include <memory>
#include <string>
#include <array>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/imu.hpp"

class ImuStripOrientationNode : public rclcpp::Node
{
public:
  ImuStripOrientationNode() : Node("imu_strip_orientation")
  {
    this->declare_parameter<std::string>("input_topic", "/unilidar/imu");
    this->declare_parameter<std::string>("output_topic", "/imu/data_raw_stripped");

    input_topic_ = this->get_parameter("input_topic").as_string();
    output_topic_ = this->get_parameter("output_topic").as_string();

    auto qos = rclcpp::QoS(rclcpp::KeepLast(10)).reliable();
    pub_ = this->create_publisher<sensor_msgs::msg::Imu>(output_topic_, qos);

    sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
      input_topic_, qos,
      std::bind(&ImuStripOrientationNode::cb, this, std::placeholders::_1)
    );

    RCLCPP_INFO(get_logger(), "Strip orientation: %s -> %s",
                input_topic_.c_str(), output_topic_.c_str());
  }

private:
  void cb(const sensor_msgs::msg::Imu::SharedPtr msg)
  {
    sensor_msgs::msg::Imu out = *msg;

    // Invalidate orientation (ROS convention)
    out.orientation.x = 0.0;
    out.orientation.y = 0.0;
    out.orientation.z = 0.0;
    out.orientation.w = 1.0;

    out.orientation_covariance = std::array<double, 9>{
      -1.0, 0.0, 0.0,
       0.0, 0.0, 0.0,
       0.0, 0.0, 0.0
    };

    pub_->publish(out);
  }

  std::string input_topic_;
  std::string output_topic_;
  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr pub_;
  rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr sub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ImuStripOrientationNode>());
  rclcpp::shutdown();
  return 0;
}