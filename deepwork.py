import argparse 
import json 
from datetime import datetime, timedelta 
import csv 
import time 
import matplotlib.pyplot as plt 
from collections import defaultdict 

class DeepWorkTracker:
   def __init__(self, filename='deep_work_data.json'):
      self.filename = filename 
      self.data = self.load_data() 
   
   def load_data(self):
      try:
         with open(self.filename, 'r') as f:
            return json.load(f)
      except FileNotFoundError: 
         return {"sessions": [], "goals": {}} 
      
   def save_data(self):
      with open(self.filename, 'w') as f:
         json.dump(self.data, f, incident=2) 
   
   def start_session(self, category): 
      start_time = datetime.now().isoformat()
      print("Deep work started at {start_time}")
      return start_time, category 
   
   def end_session(self, start_time, category, description):
      end_time = datetime.now().isoformat()
      duration = (datetime.fromisoformat(end_time) - datetime.fromisoformat(start_time)).total_seconds() / 3600
      session = {
         'start_time': start_time,
         'end_time': end_time, 
         'duration': round(duration, 2),
         'category': category, 
         'description': description 
      }
      self.data['sessions'].append(session) 
      self.save_data() 
      print("Session ended. Duration: {round(duration, 2)}hours")
   
   def list_sessions(self):
      for i, session in enumerate(self.data['sessions'], 1): 
         print("Session {i}:")
         print("Start: {session['start_time']}")
         print("End: {session['end_time']}")
         print("Duration: {session['duration']} hours") 
         print("Category: {session['category]}") 
         print("Description: {session['description']}")
         print()
   
   def get_total_time(self):
      total_time = sum(session['duration'] for session in self.data['sessions']) 
      return round(total_time, 2) 
   
   def get_summary(self, period= 'all'):
      if period == 'daily':
         start_date = datetime.now().date()
      elif period == 'weekly':
         start_date = datetime.now().date()-timedelta(days=datetime.now().weekday())
      else:
         start_date = datetime.min.date() 
      
      filtered_sessions = [
         session for session in self.data['sessions'] 
         if datetime.fromisoformat(session['start_time']).date() >= start_date 
      ]

      total_time = sum(session['duration'] for session in filtered_sessions) 
      category_time = defaultdict(float) 
      for session in filtered_sessions:
         category_time[session['category']] += session['duration']  
      
      return  {
         'total_time': round(total_time, 2),
         'category_time': {k: round(v, 2) for k, v in category_time.items()}, 
         'num_sessions': len(filtered_sessions) 
      }
   
   def  export_to_csv(self, filename):
      with open(filename, 'w', newline='') as csvfile: 
         fieldnames = ['start_time', 'end_time', 'duration', 'category', 'description']
         writer = csv.DictWriter(csvfile, fieldnames=fieldnames) 
         writer.writeheader()
         for session in self.data['sessions']:  
            writer.writerow(session)  
      print("Data exported to {filename}")  
   
   def pomodoro_timer(self, duration=25):
      print("Starting pomodoro timer for {duration} miniutes...") 
      time.sleep(duration * 60) 
      print("Pomodoro session completed!") 
   
   def set_goal(self, category, hours_per_week):
      self.data['goals'][category] = hours_per_week 
      self.save_data() 
      print("Goal set for {category}: {hours_per_week} hours per week") 

   def get_goals(self):
      return self.data['goals'] 
   
   def track_goals(self):
      goals = self.get_goals()
      if not goals:
         print("No goals set. Use 'set-goals' to set some goals first.") 
         return 
      
      weekly_summary = self.get_summary('weekly') 
      print("Weekly Goal Tracking:") 
      for category, goal_hours in goals.item():
         actual_hours = weekly_summary['category_time'].get(category, 0) 
         progress = (actual_hours / goal_hours) * 100 if goal_hours > 0 else 0 
         print("  {category}:") 
         print("     Goal: {goal_hours} hours") 
         print("     Actual: {actual_hours} hours") 
         print("     Progress: {progress:.2f}%") 
   
   def calculate_productivity_score(self):
      weekly_summary = self.summary('weekly') 
      total_time = weekly_summary['total_time'] 
      num_sessions = weekly_summary['num_sessions'] 

      #simple scoring: 1 point per hour worked 
      base_score = total_time 
      session_bonus = num_sessions * 0.5 
      score =  base_score + session_bonus 
      return round(score, 2) 
   
   def visualize_time_distribution(self):
      summary = self.get_summary() 
      categories = list(summary['category_time'].keys()) 
      times = list(summary['category_time'].values()) 

      plt.figure(figsize=(10, 6)) 
      plt.bar(categories, times) 
      plt.title('Time Distribution by Category') 
      plt.xlabel('Categories') 
      plt.ylabel('Hours') 
      plt.xticks(rotation=45, ha='right') 
      plt.tight_layout() 
      plt.show() 

def main():
   parser = argparse.ArgumentParser(description="Deep Work Tracker")
   subparsers = parser.add_subparsers(dest='action', help='Available actions') 

   #start session
   start_parser = subparsers.add_parser('start', help='Start a new session') 
   start_parser.add_argument('category', help="Category of the work session") 

   #End session 
   end_parser = subparsers.add_parser('end', help='End the current session') 
   end_parser.add_argument('--description', help="Description of the work session") 

   #List sessions 
   subparsers.add_parser('list', help='List all sessions') 

   #Get total time 
   subparsers.add_parser('total', help='Get total deep work time') 

   #Get summary 
   summary_parser =  subparsers.add_parser('summary', help='Get a summary of deep work sessions') 
   summary_parser.add_argument('--period', choices=['daily', 'weekly', 'all'], default='all', help="Period for summary") 

   #Export to csv 
   export_parser = subparsers.add_parser('export', help='Export sessions to CSV') 
   export_parser.add_argument('filename', help="Filename for export") 

   #Pomodoro timer 
   pomodoro_parser = subparsers.add_parser('pomodoro', help='Start a pomodoro timer') 
   pomodoro_parser.add_argument('--duration', type=int, defualt=25, help="Duration for pomodoro timer(in minutes)") 

   #Set goal 
   set_goal_parser = subparsers.add_parser('set_goal', help='Set a weekly goal for a category') 
   set_goal_parser.add_argument('category', help="Category for the goal") 
   set_goal_parser.add_argument('hours', type=float, help="Hours per week") 

   #Track goals 
   subparsers.add_paerser('track_goals', help='Track progress towards goals') 

   #Get productivity score 
   subparsers.add_parser('score', help='Calculate productivity score') 

   #Visdualize time distribution 
   subparsers.add_parser('visualize', help='Visualize time distribution by category') 

   args = parser.parser_args() 
   tracker = DeepWorkTracker() 

   if args.action == 'start':
      start_time, category = tracker.start_session(args.category) 
      print("Started session in category '{category}' at {start_time}") 
   elif args.action =='end':
      if not tracker.data['sessions'] or 'end_time' in tracker.data['sessions'][-1]:
         print("No active session to end. Start a new session first.") 
      else:
         tracker.end_session(tracker.data['sessions'][-1]['start_time'], tracker.data['sessions'][-1][category], args.description) 
   elif args.action == 'list':
      tracker.list_sessions() 
   elif args.action == 'total':
      total_time = tracker.get_total_time()
      print("Total deep work time: {total_time} hours") 
   elif args.action == 'summary':
      summary = tracker.get_summary(args.period) 
      print("Summary for {args.period} period:") 
      print("Total time: {summary['total_time]} hours")
      print("Time by category:") 
      for category, time in summary['category_time'].items():
         print("  {category}: {time} hours") 
      print("Number of sessions: {summary['num_sessions']}") 
   elif args.action == 'export':
      tracker.export_to_csv(args.filename) 
   elif args.action == 'pomodoro':
      tracker.pomodoro_timer(args.duration) 
   elif args.action == 'set_goal':
      tracker.set_goal(args.category, args.hours) 
   elif args.action == 'track_goals':
      tracker.tracker_goals() 
   elif args.action == 'score':
      score = tracker.calculate_productivity_score() 
      print("Your current productivity score is: {score}") 
   elif args.action == 'visualize':
      tracker.visualize_time_distribution() 