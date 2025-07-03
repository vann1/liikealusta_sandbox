def filter_accelerometer(new_pitch, new_roll, prev_pitch=None, prev_roll=None):
    if prev_pitch is None:
        return new_pitch, new_roll
    else:
        alpha = 0.1
        filtered_pitch = alpha * new_pitch + (1 - alpha) * prev_pitch
        filtered_roll = alpha * new_roll + (1 - alpha) * prev_roll
        return filtered_pitch, filtered_roll