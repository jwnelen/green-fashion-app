output "google_client_id_secret_id" {
  description = "Google client ID secret ID"
  value       = google_secret_manager_secret.google_client_id.secret_id
}

output "google_client_secret_id" {
  description = "Google client secret ID"
  value       = google_secret_manager_secret.google_client_secret.secret_id
}
