output "api_url" {
  description = "URL of the deployed API Cloud Run service"
  value       = google_cloud_run_v2_service.green_fashion_api.uri
}

output "api_name" {
  description = "Name of the API Cloud Run service"
  value       = google_cloud_run_v2_service.green_fashion_api.name
}

output "classifier_api_url" {
  description = "URL of the deployed Classifier API Cloud Run service"
  value       = google_cloud_run_v2_service.classifier_api.uri
}

output "classifier_api_name" {
  description = "Name of the Classifier API Cloud Run service"
  value       = google_cloud_run_v2_service.classifier_api.name
}
