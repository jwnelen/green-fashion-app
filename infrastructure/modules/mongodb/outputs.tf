output "mongodb_secret_id" {
  description = "Secret Manager secret ID for MongoDB URI"
  value       = data.google_secret_manager_secret.mongodb_uri.secret_id
}
