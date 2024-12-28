from time import time

class Debug:
    def __init__(self):
        self._timers = {}
        self._timers_statitics = {}
    
    def set(self, name: str):
        self._timers[name] = time()
    
    def get(self, name: str):
        init_time = self._timers.get(name, 0)

        if init_time:
            dt = time() - init_time
            min_, max_, mean, number = self._timers_statitics.get(name, (9999999, 0, 0, 0))

            if dt <= min_:
                min_ = dt
            if dt >= max_:
                max_ = dt

            self._timers_statitics[name] = min_, max_, (mean*number + dt)/(number+1), number + 1
            return dt
    
    def show_statitics(self):
        for name, (min_, max_, mean, _) in self._timers_statitics.items():
            print(f'{name}: \t min time: {(min_)*60*100:.5f}% \t max time: {(max_*60)*100:.5f}% \t mean time: {(mean*60)*100:.5f}%')