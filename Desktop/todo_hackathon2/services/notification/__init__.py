"""
Notification Service (T041)

Microservice that handles notifications for task reminders.
Subscribes to reminders topic and triggers notifications
when reminder times are reached.

Topics subscribed:
- reminders: Listens for "scheduled" and "cancelled" events

Cron binding:
- Checks pending reminders every 60s via Dapr cron binding
"""
