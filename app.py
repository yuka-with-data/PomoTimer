#----- Pomo Timer Script --------#

from flask import Flask, render_template
import time
import threading
import pygame

app = Flask(__name__, static_url_path='/static')

# define decorator
def log_method_call(func) -> callable:
    """ 
     A decorator that logs the method call and arguments.
     Parameters:
       func (function): The function to decorate.
     Returns:
       function: The decorated function.
       
       """
    def wrapper(*args, **kwargs) -> any:
        """ 
         Wrapper function that logs the method call and arguments.
         Parameters:
           *args (tuple): The positional arguments.
           **kwargs (dict): The keyword arguments.
         Returns:
           The result of the decorated function.
           """
        print(f"Calling {func.__name__} with arguments {args} and keywork arguments {kwargs}")
        return func(*args, **kwargs)
    return wrapper

class PomodoroTimer():
    def __init__(self):
        # Initialize timer-related variables
        self.timer_message = ""
        self.remaining_time = 0
        self.timer_lock = threading.Lock()  # Add a lock for thread safety
        self.cycles = 4
        self.current_session = 0
        pygame.mixer.init()

    @log_method_call
    def update_timer(self, message, time_remaining) -> None:
        """ 
         Update the timer message and remaining time.
         Parameters:
           message (str): The message to display in the timer.
           time_remaining (int): The remaining time in seconds.
         Returns:
           None.
           """
        with self.timer_lock:
            self.timer_message = message
            self.remaining_time = time_remaining
            # print(f"Timer Updated: {self.timer_message}, Remaining Time: {self.remaining_time} seconds") 
    
    @log_method_call
    def play_bell_sound(self, volume = 1.0) -> None:
        """ 
         Play bell sound
           """
        sound_path = "bell.wav"
        sound = pygame.mixer.Sound(sound_path)
        # set volume
        sound.set_volume(volume)
        # play sound
        sound.play()

    @log_method_call
    def format_time(self, seconds) -> str:
        """ 
         Format time in seconds as MM:SS
         Parameters:
           seconds (int): The time in seconds.
         Returns:
           str: The formatted time as MM:SS.
           """
        minutes, seconds = divmod(seconds, 60) # python built-in
        formatted_time = f"{minutes:02d}:{seconds:02d}"
        # print(f"Formatted Time: {formatted_time}")
        return formatted_time
    
    @log_method_call
    def countdown(self, phase, duration) -> None:
        """ 
         Run the countdown timer for the specified phase and duration.
         Parameters:
           phase (str): The phase of the timer (e.g. "Work Time" or "Break Time").
           duration (int): The duration of the timer in seconds.
         This method updates the timer display with the current phase, session couint,
         and remaining time every second during the countdown. 
         Returns:
           None.
           
           """
        start_time = time.time()

        while time.time() - start_time < duration:
            elapsed_time = time.time() - start_time
            time_remaining = max(0, int(duration - elapsed_time))

            # Update the timer with the current phase and remaining time
            session_info = f"Session {self.current_session} of {self.cycles}"
            self.update_timer(f"{phase} : {session_info} - {self.format_time(time_remaining)}", time_remaining)
            time.sleep(1)  # Update every second
            # print(f"Phase: {phase}, Elapsed Time: {elapsed_time}, Remaining Time: {time_remaining}")
    
    @log_method_call
    def pomodoro_timer(self) -> None:
        """ 
         Run the entire Pomo timer logic, including work and break phases alternating.
         Returns:
           None.
         It iterates through the specified numbe of cycles, executing the work and break phases, 
         along with brief pauses and bell sounds between each cycle.
           """
        # Display Welcome Message
        self.update_timer("Welcome to Pomo Sessions", 0)
        time.sleep(20)  # Add a pause for the welcome message
        self.play_bell_sound()

        # Iterate through the specified number of cycles
        for i in range(self.cycles):
            self.current_session = i + 1
            # Work Time
            work_phase, work_duration = "Work Time", 25 * 60
            self.countdown(work_phase, work_duration)

            if i < self.cycles - 1:
                self.play_bell_sound()

            # Add a brief pause before starting Break Time
            time.sleep(1)

            # Break Time
            break_phase, break_duration = "Break Time", 5 * 60
            self.countdown(break_phase, break_duration)

            if i < self.cycles - 1:
                self.play_bell_sound()
    
        # Display a message when the timer is finished
        self.update_timer("Great Job!", 0)

# Create an instance of the PomodoroTimer class
pomodoro_time_instance = PomodoroTimer()

# Route definition using the Flask web framework
@app.route('/')
def index():
    with pomodoro_time_instance.timer_lock:
        return render_template("index.html", timer_message=pomodoro_time_instance.timer_message)

if __name__ == '__main__':
    # Start the timer thread
    timer_thread = threading.Thread(target=pomodoro_time_instance.pomodoro_timer)
    timer_thread.start()
    # Run the Flask app in debug mode during development mode
    # Disable it in a production environment for security reasons
    app.run(debug=True)