# SYSTEMS.OS API

## GET /health
Returns runtime health status payload.

## GET /system/status
Returns summarized runtime status and registry count.

## GET /systems/registry
Returns systems registry loaded from `data/system_registry.json`.

## POST /workflows/queue
Queues workflow payload and returns `202` queue receipt.
