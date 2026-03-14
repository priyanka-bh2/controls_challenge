from . import BaseController

class Controller(BaseController):
  def __init__(self):
    self.p = 0.190
    self.i = 0.095
    self.d = -0.060
    self.error_integral = 0
    self.prev_error = 0

  def update(self, target_lataccel, current_lataccel, state, future_plan):
    error = target_lataccel - current_lataccel
    self.error_integral += error
    error_diff = error - self.prev_error
    self.prev_error = error

    pid = self.p * error + self.i * self.error_integral + self.d * error_diff

    ff = future_plan.lataccel[0] if len(future_plan.lataccel) > 0 else 0.0

    return pid + 0.34 * ff
