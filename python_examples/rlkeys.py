from dataclasses import dataclass

@dataclass
class RedisKeys:
    cartesian_task_goal_position: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::goal_position"
    cartesian_task_goal_orientation: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::goal_orientation"
    cartesian_task_current_position: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::current_position"
    mobile_base_current_position: str = "opensai::controller::Panda::cartesian_controller::mobile_base::current_position"
    mobile_base_goal_position: str = "opensai::controller::Panda::cartesian_controller::mobile_base::goal_position"
    cartesian_task_current_orientation: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::current_orientation"
    active_controller: str = "opensai::controller::Panda::active_controller_name"
    dog_current_position: str = "opensai::controller::Dog::joint_controller::joint_task::current_position"
    dog_goal_position: str = "opensai::controller::Dog::joint_controller::joint_task::goal_position"

    mobile_base_vel_otg: str = "opensai::controller::Panda::cartesian_controller::mobile_base::otg_max_velocity"
    mobile_base_acc_otg: str = "opensai::controller::Panda::cartesian_controller::mobile_base::otg_max_acceleration"

    reset: str = "sai2::interfaces::main_interface::reset"