import time

class Counter:
    def __init__(self):
        # we just being the counter here
        self.epoch_start = time.time()
    
    def get_counter(self):
        return self.epoch_start

def main():
    counter = Counter()
    print(counter.epoch_start)
    
if __name__ == "__main__":
    main()