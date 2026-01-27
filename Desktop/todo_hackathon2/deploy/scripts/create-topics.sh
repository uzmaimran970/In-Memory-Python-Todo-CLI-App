#!/bin/bash
# T012: Create Kafka Topics for Phase 5
# Prerequisites: Kafka running in cluster

set -e

echo "=== Creating Kafka Topics ==="

# Get Kafka pod name
KAFKA_POD=$(kubectl get pods -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')

if [ -z "$KAFKA_POD" ]; then
  echo "ERROR: Kafka pod not found. Ensure Kafka is running."
  exit 1
fi

echo "Using Kafka pod: $KAFKA_POD"

# Create main topics
TOPICS=("task-events" "reminders" "task-updates")
PARTITIONS=3
REPLICATION=1

for TOPIC in "${TOPICS[@]}"; do
  echo "Creating topic: $TOPIC"
  kubectl exec -it $KAFKA_POD -- kafka-topics.sh --create \
    --topic "$TOPIC" \
    --bootstrap-server localhost:9092 \
    --partitions $PARTITIONS \
    --replication-factor $REPLICATION \
    --if-not-exists
done

# Create dead-letter topics
DL_TOPICS=("task-events-deadletter" "reminders-deadletter" "task-updates-deadletter")

for TOPIC in "${DL_TOPICS[@]}"; do
  echo "Creating dead-letter topic: $TOPIC"
  kubectl exec -it $KAFKA_POD -- kafka-topics.sh --create \
    --topic "$TOPIC" \
    --bootstrap-server localhost:9092 \
    --partitions 1 \
    --replication-factor $REPLICATION \
    --if-not-exists
done

# List all topics
echo "=== Kafka Topics Created ==="
kubectl exec -it $KAFKA_POD -- kafka-topics.sh --list --bootstrap-server localhost:9092
