from prometheus_client import start_http_server, Gauge

drift_score_gauge = Gauge("log_drift_score", "Current log drift score")
alerts_total = Gauge("drift_alert_total", "Total drift alerts triggered")
centroid_updated_total = Gauge("centroid_updated_total", "Total times centroid was updated")

def start_metrics_server(port=8000):
    """Starts the Prometheus metrics server on given port."""
    start_http_server(port)
    print(f"[Metrics] Prometheus metrics server running on port {port}")

def update_drift_score(score):
    drift_score_gauge.set(score)

def increment_alerts():
    alerts_total.inc()

def increment_centroid_updates():
    centroid_updated_total.inc()