# Monitoring and alerting configuration
resource "google_monitoring_notification_channel" "email" {
  count = var.enable_monitoring ? 1 : 0

  display_name = "Green Fashion Email Notifications (${var.environment})"
  type         = "email"

  labels = {
    email_address = "alerts@example.com" # Replace with your email
  }
}

# Uptime check for the service
resource "google_monitoring_uptime_check_config" "green_fashion_uptime" {
  count = var.enable_monitoring ? 1 : 0

  display_name = "Green Fashion Uptime Check (${var.environment})"
  timeout      = "10s"
  period       = "300s"

  http_check {
    path         = "/_stcore/health"
    port         = "443"
    use_ssl      = true
    validate_ssl = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = google_cloud_run_v2_service.green_fashion_app.uri
    }
  }

  content_matchers {
    content = "ok"
    matcher = "CONTAINS_STRING"
  }
}

# Alert policy for service availability
resource "google_monitoring_alert_policy" "service_availability" {
  count = var.enable_monitoring ? 1 : 0

  display_name = "Green Fashion Service Availability (${var.environment})"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Uptime check failure"

    condition_threshold {
      filter         = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" resource.type=\"uptime_url\""
      duration       = "300s"
      comparison     = "COMPARISON_EQUAL"
      threshold_value = 0

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_NEXT_OLDER"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email[0].id]

  alert_strategy {
    auto_close = "1800s"
  }
}

# Alert policy for high error rate
resource "google_monitoring_alert_policy" "high_error_rate" {
  count = var.enable_monitoring ? 1 : 0

  display_name = "Green Fashion High Error Rate (${var.environment})"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Request error rate > 5%"

    condition_threshold {
      filter         = "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\""
      duration       = "300s"
      comparison     = "COMPARISON_GREATER_THAN"
      threshold_value = 0.05

      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = ["resource.label.service_name"]
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email[0].id]

  alert_strategy {
    auto_close = "1800s"
  }
}

# Alert policy for high memory usage
resource "google_monitoring_alert_policy" "high_memory_usage" {
  count = var.enable_monitoring ? 1 : 0

  display_name = "Green Fashion High Memory Usage (${var.environment})"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Memory utilization > 80%"

    condition_threshold {
      filter         = "metric.type=\"run.googleapis.com/container/memory/utilizations\" resource.type=\"cloud_run_revision\""
      duration       = "300s"
      comparison     = "COMPARISON_GREATER_THAN"
      threshold_value = 0.8

      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_MEAN"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = ["resource.label.service_name"]
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email[0].id]

  alert_strategy {
    auto_close = "1800s"
  }
}

# Log-based metric for application errors
resource "google_logging_metric" "app_errors" {
  count = var.enable_monitoring ? 1 : 0

  name   = "green_fashion_app_errors_${var.environment}"
  filter = <<-EOT
    resource.type="cloud_run_revision"
    resource.labels.service_name="${google_cloud_run_v2_service.green_fashion_app.name}"
    severity>=ERROR
  EOT

  metric_descriptor {
    metric_kind = "GAUGE"
    value_type  = "INT64"
    display_name = "Green Fashion Application Errors"
  }
}
