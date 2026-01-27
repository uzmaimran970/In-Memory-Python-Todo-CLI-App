"""
Audit Service (T056)

Microservice that records all task changes for audit trail.
Subscribes to task-events topic and stores change history.

Topics subscribed:
- task-events: Records all CRUD operations

Provides:
- Complete audit trail of all task modifications
- Before/after state for each change
"""
