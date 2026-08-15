import time
from datetime import datetime, timedelta
import os
import json
import threading
from core.jarvis_brain import start_agentic_loop, notification_queue


active_tasks = {}
_cron_lock = threading.Lock()

def init_cron():
    if not os.path.exists('cron_schedule.json'):
        with open('cron_schedule.json', 'w') as f:
            json.dump([], f)

def add_cron_task(task_name, task_time, prompt_to_execute):
    with _cron_lock:
        with open('cron_schedule.json', 'r') as f:
            schedule = json.load(f)

        schedule.append({
            'name': task_name,
            'time_to_next': (datetime.now() + timedelta(minutes=task_time)).isoformat(),
            'time_jumps': task_time,
            'prompt_to_execute': prompt_to_execute
        })

        with open('cron_schedule.json', 'w') as f:
            json.dump(schedule, f, indent=4)


def execute_cron_task(task_name, prompt_to_execute):
    if active_tasks.get(task_name):
        #print(f"[DEBUG] Task '{task_name}' is already running. Skipping this execution.")
        return
    
    #print(f"[DEBUG] Waking up Jarvis for cron task: {task_name}")
    #print(f"[DEBUG] Goal: {prompt_to_execute}")
    
    #notification_queue.put({
        #"type": "speak",
        #"message": f"Sir, I am now executing your scheduled task: {task_name}."
    #})
    
    active_tasks[task_name] = True

    try:
        messages_history = [{"role": "user", "content": prompt_to_execute}]
        
        start_agentic_loop(messages_history)
        
    except Exception as e:
        error_msg = str(e)
        #print(f"[DEBUG] Cron task failed: {error_msg}")
        
        with open('jarvis_errors.log', 'a') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed Cron task '{task_name}': {error_msg}\n")
            
        notification_queue.put({
            "type": "speak",
            "message": f"Sir, I encountered an error while trying to complete the scheduled task {task_name}."
        })

    finally:
        active_tasks[task_name] = False
        #print(f"[DEBUG] Finished executing cron task: {task_name}")


def check_cron_tasks():
    with _cron_lock:
        with open('cron_schedule.json', 'r') as f:
            schedule = json.load(f)

        tasks_to_run = []
        for task in schedule:
            #print(f"[DEBUG] Checking task '{task['name']}' scheduled for {task['time_to_next']}")
            if datetime.now() >= datetime.fromisoformat(task['time_to_next']):
                task['time_to_next'] = (datetime.now() + timedelta(minutes=task['time_jumps'])).isoformat()
                tasks_to_run.append((task['name'], task['prompt_to_execute']))

        with open('cron_schedule.json', 'w') as f:
            json.dump(schedule, f, indent=4)

    # Spawn threads OUTSIDE the lock to avoid holding it during execution
    for task_name, prompt in tasks_to_run:
        threading.Thread(target=execute_cron_task, args=(task_name, prompt)).start()


def start_cron_loop():
    init_cron()
    while True:
        try:
            #print(f"[DEBUG] Checking cron tasks at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            check_cron_tasks()
        except Exception as e:
            # Log error but don't let the cron loop die
            try:
                with open('jarvis_errors.log', 'a') as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Cron loop error: {str(e)}\n")
            except:
                pass
        time.sleep(60)  # 60 seconds